"""
Video Analysis Page for Visionlytics.

Allows users to upload video files (MP4, AVI, MOV), sample frames at a
configurable interval, track people across frames, predict density per frame,
and view crowd metrics over time.
"""

import os
import tempfile
import time

import cv2
import numpy as np
import pandas as pd
import streamlit as st

from app.api_client import analyze_frame_api
from app.components.charts import (
    density_distribution_pie,
    density_over_time,
    people_count_over_time,
)
from app.components.styles import (
    DENSITY_COLORS,
    header_html,
    metric_card_html,
)
from app.components.theme import DENSITY, INK
from app.database import save_analysis_record
from app.utils.draw import draw_boxes

MAX_POINTS = 1000          # timeline cap to protect browser memory
MAX_PREVIEWS = 12          # annotated frames kept for the gallery
PREVIEW_MAX_WIDTH = 640    # stored previews are downscaled to save memory
DB_SAVE_EVERY = 30         # persist every Nth sampled frame to SQLite


def _store_preview(previews: list, annotated_bgr: np.ndarray, caption: str) -> None:
    """Append a downscaled RGB preview frame, bounded by MAX_PREVIEWS."""
    if len(previews) >= MAX_PREVIEWS:
        return
    h, w = annotated_bgr.shape[:2]
    if w > PREVIEW_MAX_WIDTH:
        scale = PREVIEW_MAX_WIDTH / w
        annotated_bgr = cv2.resize(
            annotated_bgr, (PREVIEW_MAX_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA
        )
    previews.append((cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB), caption))


def _frame_stats_html(
    cur_time: float,
    people: float,
    density_label: str,
    occupancy_ratio: float,
    active_tracks: int,
) -> str:
    """HTML card summarising a processed frame."""
    density_color = DENSITY_COLORS.get(density_label, INK)
    return f"""
                <div class="section-container">
                    <h4 style="margin-top:0;">Live Frame Stats</h4>
                    <p><strong>Time:</strong> {cur_time:.1f}s</p>
                    <p><strong>People:</strong> {people}</p>
                    <p><strong>Density:</strong> <span style="color:{density_color}; font-weight:bold;">{density_label}</span></p>
                    <p><strong>Occupancy:</strong> {occupancy_ratio*100:.1f}%</p>
                    <p><strong>Active Tracks:</strong> {active_tracks}</p>
                </div>
                """


def _process_video(
    uploaded_video,
    sample_interval: int,
    min_confidence: float,
    enable_tracking: bool,
    crops: tuple,
) -> dict:
    """Run the frame-by-frame analysis and return a cacheable result dict.

    The uploaded file is only materialised to disk here (never on plain
    re-runs), and the temporary copy is always removed before returning.
    """
    crop_top, crop_bottom, crop_left, crop_right = crops

    _, ext = os.path.splitext(uploaded_video.name)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tfile:
        tfile.write(uploaded_video.read())
        video_path = tfile.name

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration_sec = total_frames / fps if total_frames > 0 else 0

    results = {
        "total_frames": total_frames,
        "fps": fps,
        "duration_sec": duration_sec,
        "frame_count": 0,
        "elapsed": 0.0,
        "timestamps": [],
        "people_counts": [],
        "densities": [],
        "confidences": [],
        "previews": [],
        "last_preview": None,
        "last_stats": None,
        "error": None,
        "completed": False,
    }

    progress_bar = st.progress(0.0)
    status_text = st.empty()
    preview_col, stats_col = st.columns([2, 1])
    preview_placeholder = preview_col.empty()
    stats_placeholder = stats_col.empty()

    approx_samples = max(1, total_frames // max(1, sample_interval))
    preview_stride = max(1, approx_samples // MAX_PREVIEWS)

    frame_idx = 0
    sampled = 0
    t_start = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Apply ROI Crop
        h, w = frame.shape[:2]
        t_crop = int(h * (crop_top / 100.0))
        b_crop = int(h * (1 - crop_bottom / 100.0))
        l_crop = int(w * (crop_left / 100.0))
        r_crop = int(w * (1 - crop_right / 100.0))

        if b_crop > t_crop and r_crop > l_crop:
            frame = frame[t_crop:b_crop, l_crop:r_crop]
        else:
            results["error"] = "Invalid crop dimensions — reduce the ROI percentages."
            break

        if frame_idx % sample_interval == 0:
            api_response = analyze_frame_api(
                frame,
                confidence=min_confidence,
                track=enable_tracking,
            )

            if api_response is None:
                results["error"] = (
                    "Lost connection to the FastAPI backend during analysis. "
                    "Results for the frames processed so far are shown below."
                )
                break

            density_label = api_response["density_label"]
            conf = api_response["confidence"]
            features = api_response["features"]
            detections = api_response["detections"]

            cur_time = frame_idx / fps
            sampled += 1

            results["timestamps"].append(cur_time)
            results["people_counts"].append(int(features["people_count"]))
            results["densities"].append(density_label)
            results["confidences"].append(conf)
            for key in ("timestamps", "people_counts", "densities", "confidences"):
                results[key] = results[key][-MAX_POINTS:]

            # Visual overlay (+ ByteTrack IDs when tracking is enabled)
            annotated = draw_boxes(frame.copy(), detections, density_level=density_label)
            if enable_tracking:
                for det in detections:
                    person_id = det.get("person_id")
                    if person_id is not None:
                        bbox = det.get("bbox", [0, 0, 0, 0])
                        cx = int((bbox[0] + bbox[2]) / 2)
                        cy = int((bbox[1] + bbox[3]) / 2)
                        cv2.putText(
                            annotated,
                            f"ID {person_id}",
                            (cx - 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (229, 70, 79),
                            2,
                        )

            active_tracks = (
                sum(1 for det in detections if det.get("person_id") is not None)
                if enable_tracking
                else 0
            )

            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            preview_placeholder.image(
                annotated_rgb,
                caption=f"Time: {cur_time:.1f}s | Frame {frame_idx}",
                width="stretch",
            )
            results["last_preview"] = annotated_rgb
            results["last_stats"] = {
                "time": cur_time,
                "people": features["people_count"],
                "density": density_label,
                "occupancy_ratio": features["occupancy_ratio"],
                "active_tracks": active_tracks,
            }
            stats_placeholder.markdown(
                _frame_stats_html(
                    cur_time,
                    features["people_count"],
                    density_label,
                    features["occupancy_ratio"],
                    active_tracks,
                ),
                unsafe_allow_html=True,
            )

            if sampled % preview_stride == 0:
                _store_preview(results["previews"], annotated, f"Time: {cur_time:.1f}s")

            # Keep the dashboard's "latest analysis" card in sync
            st.session_state["last_analysis"] = {
                "people_count": features["people_count"],
                "density": density_label,
                "occupancy_ratio": features["occupancy_ratio"],
                "confidence": conf,
                "timestamp": time.time(),
            }

            # Persist a sparse sample of frames to SQLite
            if sampled % DB_SAVE_EVERY == 0:
                save_analysis_record(
                    source_type="Video",
                    features=features,
                    density_label=density_label,
                    confidence=conf,
                )

            results["frame_count"] = sampled

        frame_idx += 1
        if total_frames > 0:
            progress_bar.progress(min(frame_idx / total_frames, 1.0))
            status_text.text(f"Processing frame {frame_idx} / {total_frames}...")

    cap.release()
    try:
        os.remove(video_path)
    except OSError:
        pass

    if results["last_preview"] is None and results["previews"]:
        results["last_preview"] = results["previews"][-1][0]

    results["elapsed"] = time.time() - t_start
    results["completed"] = results["error"] is None

    if results["completed"]:
        status_text.success(
            f"Analysis complete! Processed {results['frame_count']} frames "
            f"in {results['elapsed']:.1f}s."
        )
    else:
        status_text.warning(results["error"])

    return results

def _render_video_results(results: dict) -> None:
    """Render metrics, previews, charts and export for a finished run."""
    if results["error"]:
        st.warning(results["error"], icon=":material/cloud_off:")
    elif results["completed"]:
        throughput = results["frame_count"] / results["elapsed"] if results["elapsed"] > 0 else 0.0
        st.success(
            f"Analysis complete — {results['frame_count']} frames in "
            f"{results['elapsed']:.1f}s ({throughput:.1f} frames/s).",
            icon=":material/check_circle:",
        )

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        st.caption(f"**Total Frames:** {results['total_frames']}")
    with col_meta2:
        st.caption(f"**Frame Rate:** {results['fps']:.1f} FPS")
    with col_meta3:
        st.caption(f"**Duration:** {results['duration_sec']:.1f} seconds")

    if results["last_preview"] is not None and results["last_stats"] is not None:
        stats = results["last_stats"]
        preview_col, stats_col = st.columns([2, 1])
        with preview_col:
            st.image(results["last_preview"], caption="Last analyzed frame", width="stretch")
        with stats_col:
            st.markdown(
                _frame_stats_html(
                    stats["time"],
                    stats["people"],
                    stats["density"],
                    stats["occupancy_ratio"],
                    stats["active_tracks"],
                ),
                unsafe_allow_html=True,
            )

    if len(results["timestamps"]) == 0:
        st.info("No frames were analyzed.", icon=":material/film_off:")
        return

    timestamps = results["timestamps"]
    people_counts = results["people_counts"]
    densities = results["densities"]
    confidences = results["confidences"]

    st.markdown("---")
    st.subheader("Temporal Crowd Analytics", icon=":material/timeline:")

    avg_people = np.mean(people_counts)
    max_people = np.max(people_counts)
    min_people = np.min(people_counts)

    class_counts = {
        "LOW": densities.count("LOW"),
        "MEDIUM": densities.count("MEDIUM"),
        "HIGH": densities.count("HIGH"),
    }
    peak_density = max(class_counts, key=class_counts.get)
    peak_color = DENSITY_COLORS.get(peak_density, INK)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Avg People", f"{avg_people:.1f}", INK), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Peak People", str(max_people), DENSITY["HIGH"]), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card_html("Min People", str(min_people), DENSITY["LOW"]), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card_html("Predominant Density", peak_density, peak_color), unsafe_allow_html=True)

    st.markdown("")

    col_ch1, col_ch2 = st.columns([2, 1])
    with col_ch1:
        fig_people = people_count_over_time(timestamps, people_counts)
        st.plotly_chart(fig_people, width="stretch")

        fig_density = density_over_time(timestamps, densities)
        st.plotly_chart(fig_density, width="stretch")

    with col_ch2:
        fig_pie = density_distribution_pie(class_counts)
        st.plotly_chart(fig_pie, width="stretch")

    if results["previews"]:
        with st.expander(
            f"Sampled frames ({len(results['previews'])})",
            icon=":material/photo_library:",
        ):
            preview_cols = st.columns(3)
            for idx, (preview_rgb, caption) in enumerate(results["previews"]):
                with preview_cols[idx % 3]:
                    st.image(preview_rgb, caption=caption, width="stretch")

    video_df = pd.DataFrame({
        "Timestamp (s)": np.round(timestamps, 2),
        "People Count": people_counts,
        "Crowd Density": densities,
        "Model Confidence": np.round(confidences, 4),
    })

    csv_data = video_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Temporal Analytics CSV",
        icon=":material/download:",
        data=csv_data,
        file_name="video_crowd_analytics.csv",
        mime="text/csv",
    )

def render_video_analysis():
    """Render the Video Analysis page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Video analysis", icon=":material/movie:")
    st.markdown(
        "Upload a video file to perform automated frame-by-frame crowd tracking, "
        "density classification over time, and temporal analytics."
    )

    # ── Configuration Panel ──────────────────────────────────────────
    with st.expander("Video Processing Settings", icon=":material/tune:"):
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            sample_interval = st.slider(
                "Frame Sample Rate",
                min_value=1,
                max_value=30,
                value=5,
                help="Process every Nth frame (higher = faster, lower = denser timeline)",
            )
        with col_v2:
            min_confidence = st.slider(
                "Detection Confidence",
                min_value=0.1,
                max_value=0.9,
                value=0.35,
                step=0.05,
                help="Minimum confidence score (applied server-side)",
            )
        with col_v3:
            enable_tracking = st.checkbox(
                "Enable Person Tracking",
                value=True,
                help="Assign persistent IDs to individuals across frames using ByteTrack",
            )

    uploaded_video = st.file_uploader(
        "Choose a video file...",
        type=["mp4", "avi", "mov", "mkv"],
        help="Upload a video recording of a crowd scene",
    )

    if uploaded_video is None:
        st.info("Upload a video file to begin automated crowd analysis.", icon=":material/upload_file:")
        return

    st.caption(
        f"**File:** {uploaded_video.name} ({uploaded_video.size / 1e6:.1f} MB)"
    )

    # ── ROI Crop Controls ────────────────────────────────────────────
    with st.expander("Region of Interest (ROI) Cropping", expanded=False):
        st.write("Crop the video to ignore irrelevant areas.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            crop_top = st.slider("Crop Top %", 0, 50, 0)
        with c2:
            crop_bottom = st.slider("Crop Bottom %", 0, 50, 0)
        with c3:
            crop_left = st.slider("Crop Left %", 0, 50, 0)
        with c4:
            crop_right = st.slider("Crop Right %", 0, 50, 0)

    # ── Execution & caching ──────────────────────────────────────────
    # Streamlit re-runs this script on every interaction. Results are cached
    # under a key derived from the video + settings, so a re-run (or navigating
    # away and back) never re-processes the video.
    run_key = (
        uploaded_video.name,
        uploaded_video.size,
        sample_interval,
        round(float(min_confidence), 2),
        enable_tracking,
        crop_top,
        crop_bottom,
        crop_left,
        crop_right,
    )

    cached = st.session_state.get("video_analysis_cache")
    start_clicked = st.button(
        "Start Video Analysis",
        icon=":material/play_arrow:",
        type="primary",
    )

    results = cached["results"] if cached and cached.get("key") == run_key else None

    if results is None and cached is not None:
        st.caption("Settings changed — press **Start Video Analysis** to re-process.")

    if start_clicked and results is None:
        results = _process_video(
            uploaded_video,
            sample_interval=sample_interval,
            min_confidence=min_confidence,
            enable_tracking=enable_tracking,
            crops=(crop_top, crop_bottom, crop_left, crop_right),
        )
        st.session_state["video_analysis_cache"] = {"key": run_key, "results": results}

    if results is None:
        st.info(
            "Press **Start Video Analysis** to process this video with the current settings.",
            icon=":material/play_circle:",
        )
        return

    _render_video_results(results)
