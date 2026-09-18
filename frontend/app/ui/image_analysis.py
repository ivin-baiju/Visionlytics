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
import streamlit as st
from PIL import Image

from app.components.charts import attribute_bar_chart, region_distribution_bar
from app.components.metrics import render_analysis_metrics, render_stats_table
from app.components.styles import (
    DENSITY_COLORS,
    header_html,
    metric_card_html,
)
from frontend.app.api_client import analyze_frame_api
from frontend.app.utils.draw import draw_boxes, draw_heatmap


def render_image_analysis():
    """Render the Image Analysis page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Image analysis", icon=":material/image:")
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

    # ── ROI Crop Controls ────────────────────────────────────────────
    with st.expander("Region of Interest (ROI) Cropping", expanded=False):
        st.write("Crop the image before analysis to ignore irrelevant areas (e.g., sky, walls).")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            crop_top = st.slider("Crop Top %", 0, 50, 0)
        with c2:
            crop_bottom = st.slider("Crop Bottom %", 0, 50, 0)
        with c3:
            crop_left = st.slider("Crop Left %", 0, 50, 0)
        with c4:
            crop_right = st.slider("Crop Right %", 0, 50, 0)

    # Load image
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    # Convert RGB to BGR for OpenCV / YOLO processing
    frame_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # Apply ROI Crop
    h, w = frame_bgr.shape[:2]
    t_crop = int(h * (crop_top / 100.0))
    b_crop = int(h * (1 - crop_bottom / 100.0))
    l_crop = int(w * (crop_left / 100.0))
    r_crop = int(w * (1 - crop_right / 100.0))
    
    if b_crop > t_crop and r_crop > l_crop:
        frame_bgr = frame_bgr[t_crop:b_crop, l_crop:r_crop]
    else:
        st.error("Invalid crop dimensions!")
        return
        
    img_h, img_w = frame_bgr.shape[:2]

    # ── Detection & Analysis ─────────────────────────────────────────
    # Streamlit no longer loads ML models. FastAPI does.

    with st.spinner("Processing image and running ML inference..."):
        api_response = analyze_frame_api(frame_bgr)
        if api_response is None:
            st.error("API offline.")
            return
            
        density_label = api_response["density_label"]
        ml_confidence = api_response["confidence"]
        proba = api_response.get("probabilities", {"LOW":0, "MEDIUM":0, "HIGH":0})
        features = api_response["features"]
        detections = api_response["detections"]
        attributes_list = []

        # Prepare visualizations
        if vis_mode == "Heatmap":
            vis_bgr = draw_heatmap(frame_bgr, detections)
        elif vis_mode == "Combined (Boxes + Heatmap)":
            heat_bgr = draw_heatmap(frame_bgr, detections)
            vis_bgr = draw_boxes(heat_bgr, detections, density_label)
        else:
            vis_bgr = draw_boxes(frame_bgr.copy(), detections, density_label)

        vis_rgb = cv2.cvtColor(vis_bgr, cv2.COLOR_BGR2RGB)

        # Update session state for current view
        analysis_record = {
            "people_count": features["people_count"],
            "density": density_label,
            "occupancy_ratio": features["occupancy_ratio"],
            "confidence": ml_confidence,
            "timestamp": time.time(),
        }
        st.session_state["last_analysis"] = analysis_record

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
                <strong style="color: #FFB347;">Note:</strong> Hair and clothing colors are estimated via HSV color histogram
                analysis on detected person bounding boxes. Apparent sex is marked as UNKNOWN in accordance
                with privacy and ethical AI standards.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Attribute extraction is either disabled or no people were detected.")
