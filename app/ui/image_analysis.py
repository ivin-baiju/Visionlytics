"""
Image Analysis Page for Visionlytics.

Allows users to upload images, detect people, extract spatial features,
predict crowd density using trained ML models, and display comprehensive
visual and statistical analytics.
"""

import io
import time
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

from app.components.styles import (
    header_html,
    metric_card_html,
    density_badge_html,
    DENSITY_COLORS,
)
from app.components.metrics import render_analysis_metrics, render_stats_table
from app.components.charts import region_distribution_bar, attribute_bar_chart
from computer_vision.heatmap import generate_heatmap
from computer_vision.attributes import analyze_person_attributes
from app.resources import get_detector, get_extractor, get_predictor


def render_image_analysis():
    """Render the Image Analysis page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Image Analysis", icon=":material/image:")
    st.markdown(
        "Upload a photo to detect people, extract spatial features, "
        "and predict crowd density using trained ML algorithms."
    )

    # ── Sidebar Controls / Top Controls ─────────────────────────────
    with st.expander("Analysis Settings", icon=":material/tune:"):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            conf_threshold = st.slider(
                "Detection Confidence",
                min_value=0.1,
                max_value=0.9,
                value=0.3,
                step=0.05,
                help="Minimum confidence score for YOLO person detection",
            )
        with col_s2:
            vis_mode = st.selectbox(
                "Visualization Overlay",
                ["Bounding Boxes", "Heatmap", "Combined (Boxes + Heatmap)"],
                index=0,
            )
        with col_s3:
            enable_attributes = st.checkbox(
                "Extract Visual Attributes",
                value=True,
                help="Estimate hair color and clothing color using color histograms",
            )

    # ── File Uploader ────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png"],
        help="Upload a crowd image or public scene (JPG, JPEG, PNG)",
    )

    if uploaded_file is None:
        st.info("Upload an image to start crowd analysis.", icon=":material/upload_file:")
        return

    # Load image
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    # Convert RGB to BGR for OpenCV / YOLO processing
    frame_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    img_h, img_w = frame_bgr.shape[:2]

    # ── Detection & Analysis ─────────────────────────────────────────
    detector = get_detector(confidence_threshold=conf_threshold)
    extractor = get_extractor()
    predictor = get_predictor()

    with st.spinner("Processing image and running ML inference..."):
        t0 = time.time()
        detections = detector.detect(frame_bgr)
        detection_time = (time.time() - t0) * 1000

        # Extract features
        features = extractor.extract(detections, (img_h, img_w))

        # ML Prediction
        density_label, ml_confidence = predictor.predict(features)
        proba = predictor.predict_proba(features)

        # Attribute analysis if enabled
        attributes_list = []
        if enable_attributes and len(detections) > 0:
            for d in detections:
                attr = analyze_person_attributes(frame_bgr, d)
                attributes_list.append(attr)

        # Prepare visualizations
        if vis_mode == "Heatmap":
            vis_bgr = generate_heatmap(frame_bgr, detections, intensity=0.6)
        elif vis_mode == "Combined (Boxes + Heatmap)":
            heat_bgr = generate_heatmap(frame_bgr, detections, intensity=0.5)
            vis_bgr = detector.draw_detections(heat_bgr, detections, density_level=density_label)
        else:
            vis_bgr = detector.draw_detections(frame_bgr.copy(), detections, density_level=density_label)

        vis_rgb = cv2.cvtColor(vis_bgr, cv2.COLOR_BGR2RGB)

    # Update session state for dashboard
    analysis_record = {
        "people_count": features["people_count"],
        "density": density_label,
        "occupancy_ratio": features["occupancy_ratio"],
        "confidence": ml_confidence,
        "top_region_count": features["top_region_count"],
        "middle_region_count": features["middle_region_count"],
        "bottom_region_count": features["bottom_region_count"],
        "timestamp": time.time(),
    }
    st.session_state["last_analysis"] = analysis_record
    if "analysis_history" not in st.session_state:
        st.session_state["analysis_history"] = []
    st.session_state["analysis_history"].append(analysis_record)

    # ── Display Results ──────────────────────────────────────────────
    st.markdown("---")
    render_analysis_metrics(features, density_label, ml_confidence)
    st.markdown("")

    # Visual Comparison (Original vs Analyzed)
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.markdown("**Original Image**")
        st.image(image, width="stretch")
    with col_img2:
        st.markdown(f"**Analyzed Image ({vis_mode})**")
        st.image(vis_rgb, width="stretch")

    # Download Button
    res_buf = io.BytesIO()
    Image.fromarray(vis_rgb).save(res_buf, format="JPEG")
    st.download_button(
        label="Download Analyzed Image",
        icon=":material/download:",
        data=res_buf.getvalue(),
        file_name="visionlytics_analyzed.jpg",
        mime="image/jpeg",
    )

    st.markdown("---")

    # ── Detailed Analytics Tabs ─────────────────────────────────────
    tab_feat, tab_prob, tab_attr = st.tabs([
        ":material/scatter_plot: Spatial Features (10)",
        ":material/query_stats: ML Model Probabilities",
        ":material/palette: Visual Attributes",
    ])

    with tab_feat:
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            st.markdown("##### Extracted Feature Vector")
            feature_display = {
                "People Count": f"{int(features['people_count'])}",
                "Occupancy Ratio": f"{features['occupancy_ratio'] * 100:.2f}%",
                "Avg Person Area": f"{features['avg_person_area'] * 100:.2f}%",
                "Avg Normalized Distance": f"{features['avg_distance']:.4f}",
                "Min Normalized Distance": f"{features['min_distance']:.4f}",
                "Spatial Spread (StdDev)": f"{features['spatial_spread']:.4f}",
                "Top Region Count": f"{int(features['top_region_count'])}",
                "Middle Region Count": f"{int(features['middle_region_count'])}",
                "Bottom Region Count": f"{int(features['bottom_region_count'])}",
                "Frame Occupancy Density": f"{features['frame_occupancy_density']:.4f}",
            }
            render_stats_table(feature_display)

        with col_f2:
            st.markdown("##### Regional Distribution")
            fig_reg = region_distribution_bar(
                int(features["top_region_count"]),
                int(features["middle_region_count"]),
                int(features["bottom_region_count"]),
            )
            st.plotly_chart(fig_reg, width="stretch")

    with tab_prob:
        st.markdown("##### Class Probability Distribution")
        prob_cols = st.columns(3)
        for idx, (cls_name, prob_val) in enumerate(proba.items()):
            color = DENSITY_COLORS.get(cls_name, "#ffffff")
            with prob_cols[idx]:
                st.markdown(
                    metric_card_html(f"{cls_name} Probability", f"{prob_val*100:.1f}%", color),
                    unsafe_allow_html=True,
                )

        st.caption(
            f"Prediction generated by **{predictor.model_name.replace('_', ' ').title()}**. "
            f"Inference & detection latency: {detection_time:.1f} ms."
        )

    with tab_attr:
        if enable_attributes and len(attributes_list) > 0:
            hair_counts = {}
            clothing_counts = {}
            for a in attributes_list:
                hc = a.get("hair_color", "UNKNOWN")
                cc = a.get("clothing_color", "UNKNOWN")
                hair_counts[hc] = hair_counts.get(hc, 0) + 1
                clothing_counts[cc] = clothing_counts.get(cc, 0) + 1

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                fig_hair = attribute_bar_chart(hair_counts, "Estimated Hair Color")
                st.plotly_chart(fig_hair, width="stretch")
            with col_a2:
                fig_cloth = attribute_bar_chart(clothing_counts, "Estimated Clothing Color")
                st.plotly_chart(fig_cloth, width="stretch")

            st.markdown("""
            <div class="info-box" style="font-size: 0.8rem;">
                <strong style="color: #f39c12;">Note:</strong> Hair and clothing colors are estimated via HSV color histogram
                analysis on detected person bounding boxes. Apparent sex is marked as UNKNOWN in accordance
                with privacy and ethical AI standards.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Attribute extraction is either disabled or no people were detected.")
