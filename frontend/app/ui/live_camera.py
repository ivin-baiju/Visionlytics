"""
Live Camera Page for Visionlytics.

Provides real-time crowd analytics using an attached webcam or USB camera feed.
Displays real-time bounding boxes, live crowd density classification,
occupancy metrics, and FPS tracking.
"""

import time

import cv2
import numpy as np
import streamlit as st

from app.api_client import analyze_frame_api
from app.components.metrics import render_analysis_metrics
from app.components.styles import (
    DENSITY_COLORS,
    header_html,
)
from app.components.theme import INK, LIME_DARK, MUTED
from app.database import save_analysis_record
from app.utils.draw import draw_boxes, draw_heatmap

DB_SAVE_EVERY = 30  # persist at most one live-camera record per N frames


def _draw_track_ids(frame_bgr: np.ndarray, detections: list) -> np.ndarray:
    """Draw ByteTrack IDs above each detection that has a person_id."""
    for det in detections:
        person_id = det.get("person_id")
        if person_id is None:
            continue
        bbox = det.get("bbox", [0, 0, 0, 0])
        cx = int((bbox[0] + bbox[2]) / 2)
        cy = int((bbox[1] + bbox[3]) / 2)
        cv2.putText(
            frame_bgr,
            f"ID {person_id}",
            (cx - 10, max(cy - 10, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (229, 70, 79),
            2,
        )
    return frame_bgr


def render_live_camera():
    """Render the Live Camera page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Live camera analytics", icon=":material/videocam:")
    st.markdown(
        "Stream live video from your local webcam to perform real-time person detection, "
        "spatial feature extraction, and instant crowd density inference."
    )

    # ── Controls ─────────────────────────────────────────────────────
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        camera_id = st.number_input("Camera Device Index", min_value=0, max_value=5, value=0, step=1)
    with col_c2:
        min_confidence = st.slider(
            "Confidence Threshold",
            0.1,
            0.9,
            0.35,
            0.05,
            help="Applied server-side during inference",
        )
    with col_c3:
        vis_mode = st.selectbox(
            "Visualization Mode",
            ["Bounding Boxes", "Heatmap", "Combined (Boxes + Heatmap)"],
            index=0,
        )
    with col_c4:
        enable_tracking = st.toggle(
            "Enable Tracking",
            value=True,
            help="Assign persistent ByteTrack IDs to each person (server-side)",
        )

    col_btn1, _col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_camera = st.toggle("Start Live Feed", value=False)

    if not run_camera:
        st.info("Toggle the switch above to activate your camera.", icon=":material/videocam:")

        # Alternative: Snapshot mode with st.camera_input for browsers/headless setups
        with st.expander("Or take a snapshot using browser camera", icon=":material/photo_camera:"):
            cam_picture = st.camera_input("Take a snapshot")
            if cam_picture is not None:
                bytes_data = cam_picture.getvalue()
                cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

                with st.spinner("Analyzing snapshot via backend inference..."):
                    api_response = analyze_frame_api(
                        cv_img,
                        confidence=min_confidence,
                        track=enable_tracking,
                    )

                if api_response is None:
                    st.error(
                        "Backend API is unreachable — snapshot analysis requires the "
                        "FastAPI service to be running.",
                        icon=":material/cloud_off:",
                    )
                    return

                density_label = api_response["density_label"]
                conf = api_response["confidence"]
                features = api_response["features"]
                detections = api_response["detections"]

                annotated = draw_boxes(cv_img.copy(), detections, density_level=density_label)
                if enable_tracking:
                    annotated = _draw_track_ids(annotated, detections)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

                st.markdown("---")
                render_analysis_metrics(features, density_label, conf)
                st.image(
                    annotated_rgb,
                    caption=f"Analyzed Snapshot: {density_label} Density",
                    width="stretch",
                )

                # Save to SQLite database
                save_analysis_record(
                    source_type="Live Camera",
                    features=features,
                    density_label=density_label,
                    confidence=conf,
                )

                # Update session state for current view
                st.session_state["last_analysis"] = {
                    "people_count": features["people_count"],
                    "density": density_label,
                    "occupancy_ratio": features["occupancy_ratio"],
                    "confidence": conf,
                    "timestamp": time.time(),
                }
        return

    # ── Live Video Loop ──────────────────────────────────────────────
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        st.error(
            f"Unable to access camera device index {camera_id}. "
            "Please ensure camera permissions are granted or try another device index.",
            icon=":material/videocam_off:",
        )
        return

    # Streamlit no longer loads ML models. FastAPI does.

    feed_col, metrics_col = st.columns([3, 1])
    feed_placeholder = feed_col.empty()
    metrics_placeholder = metrics_col.empty()

    prev_time = time.time()
    fps_history = []
    frame_count = 0

    try:
        while run_camera:
            ret, frame = cap.read()
            if not ret:
                feed_placeholder.warning("Failed to grab frame from camera stream.", icon=":material/warning:")
                break

            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            fps_history.append(fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = np.mean(fps_history)

            # Call FastAPI
            api_response = analyze_frame_api(
                frame,
                confidence=min_confidence,
                track=enable_tracking,
            )
            if api_response is None:
                st.error("API disconnected.")
                break
                
            density_label = api_response["density_label"]
            conf = api_response["confidence"]
            features = api_response["features"]
            detections = api_response["detections"]

            # Visualization
            if vis_mode == "Heatmap":
                vis_frame = draw_heatmap(frame, detections)
            elif vis_mode == "Combined (Boxes + Heatmap)":
                heat = draw_heatmap(frame, detections)
                vis_frame = draw_boxes(heat, detections, density_label)
            else:
                vis_frame = draw_boxes(frame.copy(), detections, density_label)

            if enable_tracking:
                vis_frame = _draw_track_ids(vis_frame, detections)

            # Render FPS on frame
            cv2.putText(
                vis_frame,
                f"FPS: {avg_fps:.1f}",
                (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (175, 175, 175),
                2,
            )

            frame_rgb = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            feed_placeholder.image(frame_rgb, channels="RGB", width="stretch")

            # Persist sparsely to avoid hammering the database
            frame_count += 1
            if frame_count % DB_SAVE_EVERY == 0:
                save_analysis_record(
                    source_type="Live Camera",
                    features=features,
                    density_label=density_label,
                    confidence=conf
                )

            # Update session state for dashboard
            st.session_state["last_analysis"] = {
                "people_count": features["people_count"],
                "density": density_label,
                "occupancy_ratio": features["occupancy_ratio"],
                "confidence": conf,
                "timestamp": time.time(),
            }

            active_tracks = (
                sum(1 for det in detections if det.get("person_id") is not None)
                if enable_tracking
                else 0
            )
            track_card = ""
            if enable_tracking:
                track_card = f"""
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Active Tracks</div>
                <div class="metric-value" style="color: {LIME_DARK};">{active_tracks}</div>
            </div>"""

            density_color = DENSITY_COLORS.get(density_label, INK)
            metrics_placeholder.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">People Detected</div>
                <div class="metric-value" style="color: {INK};">{features['people_count']}</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Crowd Density</div>
                <div class="metric-value" style="color: {density_color};">{density_label}</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Occupancy</div>
                <div class="metric-value" style="color: {MUTED};">{features['occupancy_ratio']*100:.1f}%</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Model Confidence</div>
                <div class="metric-value" style="color: {LIME_DARK};">{conf*100:.1f}%</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Stream Rate</div>
                <div class="metric-value" style="color: {LIME_DARK};">{avg_fps:.1f} FPS</div>
            </div>
            {track_card}
            """, unsafe_allow_html=True)

            # Add small delay to keep CPU utilization sane
            time.sleep(0.01)

    finally:
        cap.release()
