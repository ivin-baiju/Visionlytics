"""
Video Analysis Page for Visionlytics.

Allows users to upload video files (MP4, AVI, MOV), sample frames at a
configurable interval, track people across frames, predict density per frame,
and view crowd metrics over time.
"""

import collections
import os
import tempfile
import time

import cv2
import numpy as np
import pandas as pd
import streamlit as st

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
from frontend.app.api_client import analyze_frame_api


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
            conf_threshold = st.slider(
                "Detection Confidence",
                min_value=0.1,
                max_value=0.9,
                value=0.35,
                step=0.05,
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

    # Save uploaded video to temporary file
    _, ext = os.path.splitext(uploaded_video.name)
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tfile.write(uploaded_video.read())
    tfile.close()
    video_path = tfile.name

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration_sec = total_frames / fps if total_frames > 0 else 0

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        st.caption(f"**Total Frames:** {total_frames}")
    with col_meta2:
        st.caption(f"**Frame Rate:** {fps:.1f} FPS")
    with col_meta3:
        st.caption(f"**Duration:** {duration_sec:.1f} seconds")

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

    if st.button("Start Video Analysis", icon=":material/play_arrow:", type="primary"):

        progress_bar = st.progress(0.0)
        status_text = st.empty()
        preview_col, stats_col = st.columns([2, 1])

        preview_placeholder = preview_col.empty()
        stats_placeholder = stats_col.empty()

        timestamps = []
        people_counts = []
        densities = []
        confidences = []

        frame_idx = 0
        frame_count = 0
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
                st.error("Invalid crop dimensions!")
                break

            if frame_idx % sample_interval == 0:
                # Call FastAPI backend
                api_response = analyze_frame_api(frame)
                
                if api_response is None:
                    st.error("Failed to connect to FastAPI backend. Is it running?")
                    break

                density_label = api_response["density_label"]
                conf = api_response["confidence"]
                features = api_response["features"]
                detections = api_response["detections"]

                cur_time = frame_idx / fps
                timestamps.append(cur_time)
                people_counts.append(int(features["people_count"]))
                densities.append(density_label)
                confidences.append(conf)

                # Cap lists to prevent browser memory exhaustion on long videos
                MAX_POINTS = 1000
                timestamps = timestamps[-MAX_POINTS:]
                people_counts = people_counts[-MAX_POINTS:]
                densities = densities[-MAX_POINTS:]
                confidences = confidences[-MAX_POINTS:]

                # Visual overlay
                annotated = detector.draw_detections(frame.copy(), detections, density_level=density_label)
                if enable_tracking:
                    for det in detections:
                        if det.person_id is not None:
                            cx, cy = int(det.center[0]), int(det.center[1])
                            cv2.putText(
                                annotated,
                                f"ID {det.person_id}",
                                (cx - 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 255),
                                2,
                            )

                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                preview_placeholder.image(annotated_rgb, caption=f"Time: {cur_time:.1f}s | Frame {frame_idx}", width="stretch")

                # Live metrics
                active_tracks = sum(1 for det in detections if det.person_id is not None) if enable_tracking else 0
                density_color = DENSITY_COLORS.get(density_label, "#1a2340")
                stats_placeholder.markdown(f"""
                <div class="section-container">
                    <h4 style="margin-top:0;">Live Frame Stats</h4>
                    <p><strong>Time:</strong> {cur_time:.1f}s</p>
                    <p><strong>People:</strong> {features['people_count']}</p>
                    <p><strong>Density:</strong> <span style="color:{density_color}; font-weight:bold;">{density_label}</span></p>
                    <p><strong>Occupancy:</strong> {features['occupancy_ratio']*100:.1f}%</p>
                    <p><strong>Active Tracks:</strong> {active_tracks}</p>
                </div>
                """, unsafe_allow_html=True)

                # Update session state for current view
                analysis_record = {
                    "people_count": features["people_count"],
                    "density": density_label,
                    "occupancy_ratio": features["occupancy_ratio"],
                    "confidence": conf,
                    "timestamp": time.time(),
                }
                st.session_state["last_analysis"] = analysis_record
                
                # Save to SQLite
                if frame_count % 30 == 0:  # Save 1 frame every second approx to DB
                    save_analysis_record(
                        source_type="Video",
                        features=features,
                        density_label=density_label,
                        confidence=conf
                    )

                frame_count += 1

            frame_idx += 1
            if total_frames > 0:
                progress_bar.progress(min(frame_idx / total_frames, 1.0))
                status_text.text(f"Processing frame {frame_idx} / {total_frames}...")

        cap.release()
        try:
            os.remove(video_path)
        except Exception:
            pass

        elapsed = time.time() - t_start
        status_text.success(f"Analysis complete! Processed {frame_count} frames in {elapsed:.1f}s.")

        if len(timestamps) > 0:
            st.markdown("---")
            st.subheader("Temporal Crowd Analytics", icon=":material/timeline:")

            # High-level summary metrics
            avg_people = np.mean(people_counts)
            max_people = np.max(people_counts)
            min_people = np.min(people_counts)

            # Class frequencies
            class_counts = {
                "LOW": densities.count("LOW"),
                "MEDIUM": densities.count("MEDIUM"),
                "HIGH": densities.count("HIGH"),
            }
            peak_density = max(class_counts, key=class_counts.get)
            peak_color = DENSITY_COLORS.get(peak_density, "#1a2340")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(metric_card_html("Avg People", f"{avg_people:.1f}", "#4A7DFF"), unsafe_allow_html=True)
            with c2:
                st.markdown(metric_card_html("Peak People", str(max_people), "#FF6B6B"), unsafe_allow_html=True)
            with c3:
                st.markdown(metric_card_html("Min People", str(min_people), "#2ECDA7"), unsafe_allow_html=True)
            with c4:
                st.markdown(metric_card_html("Predominant Density", peak_density, peak_color), unsafe_allow_html=True)

            st.markdown("")

            # Charts
            col_ch1, col_ch2 = st.columns([2, 1])
            with col_ch1:
                fig_people = people_count_over_time(timestamps, people_counts)
                st.plotly_chart(fig_people, width="stretch")

                fig_density = density_over_time(timestamps, densities)
                st.plotly_chart(fig_density, width="stretch")

            with col_ch2:
                fig_pie = density_distribution_pie(class_counts)
                st.plotly_chart(fig_pie, width="stretch")

            # Exportable summary table
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
