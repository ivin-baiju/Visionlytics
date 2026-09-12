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

from app.components.styles import (
    header_html,
    metric_card_html,
    DENSITY_COLORS,
)
from app.components.metrics import render_analysis_metrics
from computer_vision.heatmap import generate_heatmap
from app.resources import get_detector, get_extractor, get_predictor
from app.database import save_analysis_record


def render_live_camera():
    """Render the Live Camera page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Live Camera Analytics", icon=":material/videocam:")
    st.markdown(
        "Stream live video from your local webcam to perform real-time person detection, "
        "spatial feature extraction, and instant crowd density inference."
    )

    # ── Controls ─────────────────────────────────────────────────────
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        camera_id = st.number_input("Camera Device Index", min_value=0, max_value=5, value=0, step=1)
    with col_c2:
        conf_threshold = st.slider("Confidence Threshold", 0.1, 0.9, 0.35, 0.05)
    with col_c3:
        vis_mode = st.selectbox(
            "Visualization Mode",
            ["Bounding Boxes", "Heatmap", "Combined (Boxes + Heatmap)"],
            index=0,
        )

    col_btn1, col_btn2 = st.columns([1, 4])
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
                h, w = cv_img.shape[:2]

                detector = get_detector(confidence_threshold=conf_threshold)
                extractor = get_extractor()
                predictor = get_predictor()

                detections = detector.detect(cv_img)
                features = extractor.extract(detections, (h, w))
                density_label, conf = predictor.predict(features)

                annotated = detector.draw_detections(cv_img.copy(), detections, density_level=density_label)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

                st.markdown("---")
                render_analysis_metrics(features, density_label, conf)
                st.image(annotated_rgb, caption=f"Analyzed Snapshot: {density_label} Density", width="stretch")
                
                # Save to SQLite database
                save_analysis_record(
                    source_type="Live Camera",
                    features=features,
                    density_label=density_label,
                    confidence=conf
                )
                
                # Update session state for current view
                analysis_record = {
                    "people_count": features["people_count"],
                    "density": density_label,
                    "occupancy_ratio": features["occupancy_ratio"],
                    "confidence": conf,
                    "timestamp": time.time(),
                }
                st.session_state["last_analysis"] = analysis_record
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

    detector = get_detector(confidence_threshold=conf_threshold)
    extractor = get_extractor()
    predictor = get_predictor()

    feed_col, metrics_col = st.columns([3, 1])
    feed_placeholder = feed_col.empty()
    metrics_placeholder = metrics_col.empty()

    prev_time = time.time()
    fps_history = []

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

            h, w = frame.shape[:2]
            detections = detector.detect(frame)
            features = extractor.extract(detections, (h, w))
            density_label, conf = predictor.predict(features)

            # Visualization
            if vis_mode == "Heatmap":
                vis_frame = generate_heatmap(frame, detections, intensity=0.6)
            elif vis_mode == "Combined (Boxes + Heatmap)":
                heat = generate_heatmap(frame, detections, intensity=0.5)
                vis_frame = detector.draw_detections(heat, detections, density_level=density_label)
            else:
                vis_frame = detector.draw_detections(frame.copy(), detections, density_level=density_label)

            # Render FPS on frame
            cv2.putText(
                vis_frame,
                f"FPS: {avg_fps:.1f}",
                (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            frame_rgb = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            feed_placeholder.image(frame_rgb, channels="RGB", width="stretch")

            # Save to SQLite occasionally (e.g. once every ~30 frames) to avoid DB spam
            if int(curr_time) % 2 == 0:
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

            density_color = DENSITY_COLORS.get(density_label, "#ffffff")
            metrics_placeholder.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">People Detected</div>
                <div class="metric-value" style="color: #636ee6;">{features['people_count']}</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Crowd Density</div>
                <div class="metric-value" style="color: {density_color};">{density_label}</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Occupancy</div>
                <div class="metric-value" style="color: #a29bfe;">{features['occupancy_ratio']*100:.1f}%</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Model Confidence</div>
                <div class="metric-value" style="color: #ffeaa7;">{conf*100:.1f}%</div>
            </div>
            <div class="metric-card" style="margin-top: 10px;">
                <div class="metric-label">Stream Rate</div>
                <div class="metric-value" style="color: #00b894;">{avg_fps:.1f} FPS</div>
            </div>
            """, unsafe_allow_html=True)

            # Add small delay to keep CPU utilization sane
            time.sleep(0.01)

    finally:
        cap.release()
