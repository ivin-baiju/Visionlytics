"""
Dashboard Page for Visionlytics.

Displays a premium overview of the system with animated feature cards,
metric summaries, system status indicators, and architecture overview.
"""

import streamlit as st
from app.components.styles import (
    header_html,
    metric_card_html,
    status_card_html,
    feature_card_html,
    arch_card_html,
    DENSITY_COLORS,
)
from app.components.icons import (
    ICON_IMAGE_ANALYSIS,
    ICON_VIDEO_ANALYSIS,
    ICON_LIVE_CAMERA,
    ICON_COMPUTER_VISION,
    ICON_FEATURE_ENGINEERING,
    ICON_MACHINE_LEARNING,
)
from app.components.charts import density_distribution_pie, region_distribution_bar


def render_dashboard():
    """Render the main dashboard page."""
    st.markdown(header_html(), unsafe_allow_html=True)

    # ── Quick Start Section ─────────────────────────────────────────
    st.subheader("Quick Start", icon=":material/rocket_launch:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            feature_card_html(
                ICON_IMAGE_ANALYSIS,
                "Image Analysis",
                "Upload a photo to detect people and analyze crowd density with spatial heatmaps",
                "#636ee6",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            feature_card_html(
                ICON_VIDEO_ANALYSIS,
                "Video Analysis",
                "Upload a video to track people and view density changes over time",
                "#a29bfe",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            feature_card_html(
                ICON_LIVE_CAMERA,
                "Live Camera",
                "Real-time crowd analysis using your webcam feed with instant density classification",
                "#00b894",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Latest Analysis Summary ────────────────────────────────────
    if "last_analysis" in st.session_state:
        st.subheader("Latest Analysis", icon=":material/insights:")
        analysis = st.session_state["last_analysis"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                metric_card_html(
                    "People Detected",
                    str(int(analysis.get("people_count", 0))),
                    "#636ee6",
                ),
                unsafe_allow_html=True,
            )

        with col2:
            density = analysis.get("density", "N/A")
            color = DENSITY_COLORS.get(density, "#ffffff")
            st.markdown(
                metric_card_html("Crowd Density", density, color),
                unsafe_allow_html=True,
            )

        with col3:
            occ = analysis.get("occupancy_ratio", 0)
            st.markdown(
                metric_card_html("Occupancy", f"{occ*100:.1f}%", "#a29bfe"),
                unsafe_allow_html=True,
            )

        with col4:
            conf = analysis.get("confidence", 0)
            st.markdown(
                metric_card_html("Confidence", f"{conf*100:.1f}%", "#ffeaa7"),
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Charts row
        col_a, col_b = st.columns(2)

        with col_a:
            # Density distribution (if we have history)
            if "analysis_history" in st.session_state:
                history = st.session_state["analysis_history"]
                counts = {}
                for h in history:
                    d = h.get("density", "N/A")
                    counts[d] = counts.get(d, 0) + 1
                fig = density_distribution_pie(counts)
                st.plotly_chart(fig, width="stretch")

        with col_b:
            # Regional distribution
            if "last_analysis" in st.session_state:
                a = st.session_state["last_analysis"]
                fig = region_distribution_bar(
                    int(a.get("top_region_count", 0)),
                    int(a.get("middle_region_count", 0)),
                    int(a.get("bottom_region_count", 0)),
                )
                st.plotly_chart(fig, width="stretch")

    else:
        # No analysis yet — welcome message
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
            <strong>Welcome to Visionlytics!</strong><br>
            No analysis has been performed yet. Use the sidebar to navigate to
            <strong>Image Analysis</strong>, <strong>Video Analysis</strong>, or
            <strong>Live Camera</strong> to get started.
        </div>
        """, unsafe_allow_html=True)

    # ── System Status Panel ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("System Status", icon=":material/tune:")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(status_card_html("Core Backend", "Online"), unsafe_allow_html=True)
    with col_s2:
        st.markdown(status_card_html("YOLOv8s Engine", "Ready"), unsafe_allow_html=True)
    with col_s3:
        st.markdown(status_card_html("ML Classifiers", "7 Loaded"), unsafe_allow_html=True)
    with col_s4:
        st.markdown(status_card_html("Tracker", "Active"), unsafe_allow_html=True)

    # ── System Architecture ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("System Architecture", icon=":material/account_tree:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            arch_card_html(
                ICON_COMPUTER_VISION,
                "Computer Vision",
                [
                    "YOLOv8s Person Detection",
                    "Bounding Box Visualization",
                    "Gaussian Heatmap Generation",
                    "Centroid-based Tracking",
                    "Visual Attribute Estimation",
                ],
                "#636ee6",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            arch_card_html(
                ICON_FEATURE_ENGINEERING,
                "Feature Engineering",
                [
                    "People Count & Occupancy",
                    "Spatial Distance Metrics",
                    "Regional Distribution (3-zone)",
                    "Frame Occupancy Density",
                    "10 Features Total",
                ],
                "#a29bfe",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            arch_card_html(
                ICON_MACHINE_LEARNING,
                "Machine Learning",
                [
                    "Logistic Regression & KNN",
                    "Decision Tree & Random Forest",
                    "SVM with RBF Kernel",
                    "Gradient Boosting",
                    "Voting Ensemble (Meta-learner)",
                ],
                "#00b894",
            ),
            unsafe_allow_html=True,
        )
