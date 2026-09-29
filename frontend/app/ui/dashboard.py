"""
Dashboard Page for Visionlytics.

Displays a flat overview of the system with dense metric cards,
an analyses filter panel, system status indicators, and architecture overview.
"""

import pandas as pd
import streamlit as st

from app.components.charts import (
    density_distribution_pie,
    people_count_over_time,
)
from app.components.icons import (
    ICON_COMPUTER_VISION,
    ICON_FEATURE_ENGINEERING,
    ICON_IMAGE_ANALYSIS,
    ICON_LIVE_CAMERA,
    ICON_MACHINE_LEARNING,
    ICON_VIDEO_ANALYSIS,
)
from app.components.styles import (
    DENSITY_COLORS,
    arch_card_html,
    feature_card_html,
    header_html,
    metric_card_html,
    status_card_html,
)
from app.components.theme import INK, LIME_DARK, MUTED
from app.database import get_recent_history


def render_dashboard():
    """Render the main dashboard page."""
    st.markdown(header_html(), unsafe_allow_html=True)

    # ── Quick Start Section ─────────────────────────────────────────
    st.subheader("Quick start", icon=":material/rocket_launch:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            feature_card_html(
                ICON_IMAGE_ANALYSIS,
                "Image Analysis",
                "Upload a photo to detect people and analyze crowd density with spatial heatmaps",
                INK,
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            feature_card_html(
                ICON_VIDEO_ANALYSIS,
                "Video Analysis",
                "Upload a video to track people and view density changes over time",
                MUTED,
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            feature_card_html(
                ICON_LIVE_CAMERA,
                "Live Camera",
                "Real-time crowd analysis using your webcam feed with instant density classification",
                LIME_DARK,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Latest Analysis Summary ────────────────────────────────────
    history = get_recent_history(limit=50)
    
    if "last_analysis" in st.session_state:
        analysis = st.session_state["last_analysis"]
    elif history:
        analysis = history[0]
        # map db column to what dashboard expects
        if "density_label" in analysis and "density" not in analysis:
            analysis["density"] = analysis["density_label"]
    else:
        analysis = None

    # ── Zone 2: Analyses filter panel ─────────────────────────────────
    st.subheader("Analyses", icon=":material/filter_list:")

    status_filter = st.segmented_control(
        "Status",
        options=["All", "LOW", "MEDIUM", "HIGH"],
        default="All",
        key="dashboard_status_filter",
    )
    source_filter = st.segmented_control(
        "Source",
        options=["All", "Image", "Video", "Live Camera"],
        default="All",
        key="dashboard_source_filter",
    )

    filtered = list(history)
    if status_filter and status_filter != "All":
        filtered = [h for h in filtered if h.get("density_label") == status_filter]
    norm_source = (source_filter or "All").lower()
    if norm_source != "all":
        filtered = [
            h
            for h in filtered
            if norm_source in str(h.get("source_type", "")).lower()
        ]

    if filtered:
        st.markdown('<div class="analyses-panel">', unsafe_allow_html=True)
        st.caption(f"{len(filtered)} of {len(history)} records")
        st.dataframe(
            [
                {
                    "Time": h.get("timestamp", ""),
                    "Source": h.get("source_type", ""),
                    "People": h.get("people_count", 0),
                    "Density": h.get("density_label", ""),
                    "Confidence": f"{float(h.get('confidence', 0)) * 100:.1f}%",
                }
                for h in filtered[:20]
            ],
            width="stretch",
            height=280,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No analyses match the selected filters.", icon=":material/search_off:")

        st.markdown("---")

    # ── Zone 3: Analysis history & trends ────────────────────────────


    if analysis:
        st.subheader("Latest analysis", icon=":material/insights:")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                metric_card_html(
                    "People Detected",
                    str(int(analysis.get("people_count", 0))),
                    INK,
                ),
                unsafe_allow_html=True,
            )

        with col2:
            density = analysis.get("density", "N/A")
            color = DENSITY_COLORS.get(density, INK)
            st.markdown(
                metric_card_html("Crowd Density", density, color),
                unsafe_allow_html=True,
            )

        with col3:
            occ = analysis.get("occupancy_ratio", 0)
            st.markdown(
                metric_card_html("Occupancy", f"{float(occ) * 100:.1f}%", MUTED),
                unsafe_allow_html=True,
            )

        with col4:
            conf = analysis.get("confidence", 0)
            st.markdown(
                metric_card_html("Confidence", f"{conf*100:.1f}%", LIME_DARK),
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Charts row
        col_a, col_b = st.columns(2)

        with col_a:
            # Density distribution (if we have history)
            history = get_recent_history(limit=50)
            if history:
                counts = {}
                for h in history:
                    d = h.get("density_label", "N/A")
                    counts[d] = counts.get(d, 0) + 1
                fig = density_distribution_pie(counts)
                st.plotly_chart(fig, width="stretch")

        with col_b:
            # People count trend across recorded analyses (oldest → newest)
            if history:
                df = pd.DataFrame(history)
                if "people_count" in df.columns and len(df) > 0:
                    counts = df["people_count"].tolist()[::-1]  # history is DESC
                    fig_line = people_count_over_time(list(range(len(counts))), counts)
                    st.plotly_chart(fig_line, width="stretch")

    else:
        # No analysis yet — welcome message
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
            <strong>Welcome to Visionlytics!</strong><br>
            No analysis has been performed yet. Use the sidebar to navigate to
            <strong>Image analysis</strong>, <strong>Video analysis</strong>, or
            <strong>Live camera</strong> to get started.
        </div>
        """, unsafe_allow_html=True)

    # ── System Status Panel ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("System status", icon=":material/tune:")
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
    st.subheader("System architecture", icon=":material/account_tree:")

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
                INK,
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
                MUTED,
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
                LIME_DARK,
            ),
            unsafe_allow_html=True,
        )
