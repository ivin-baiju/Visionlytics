"""
Dataset Exploration Page for Visionlytics.

Provides interactive dataset exploration, descriptive statistics,
class distributions, feature correlation heatmaps, distribution histograms,
and dataset regeneration controls.
"""

import os
import pandas as pd
import streamlit as st

from app.components.styles import header_html, metric_card_html
from app.components.charts import (
    class_distribution_bar,
    feature_correlation_heatmap,
    feature_distribution_histogram,
    scatter_feature_vs_density,
)
from machine_learning.preprocessing import (
    load_dataset,
    DATASET_PATH,
    FEATURE_COLUMNS,
    LABEL_CLASSES,
)
from dataset.generate_dataset import generate_dataset


def render_dataset_page():
    """Render the Dataset Exploration page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Dataset Exploration & Analytics", icon=":material/dataset:")
    st.markdown(
        "Inspect the training dataset, examine feature distributions, "
        "verify class balance, and study spatial correlation patterns."
    )

    # ── Dataset Controls ─────────────────────────────────────────────
    with st.expander("Dataset Generation Controls", icon=":material/settings:"):
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        with col_ctrl1:
            n_per_class = st.number_input(
                "Samples per class",
                min_value=100, max_value=50000, value=500, step=100,
                help="LOW, MEDIUM, and HIGH classes will each have this many samples."
            )
        with col_ctrl2:
            confirm_overwrite = st.checkbox(
                "Confirm Overwrite",
                help="Check this box to confirm overwriting the existing dataset."
            )
        with col_ctrl3:
            st.write("") # Spacer
            st.write("") # Spacer
            regenerate = st.button("Regenerate Dataset", icon=":material/refresh:", type="primary" if confirm_overwrite else "secondary", disabled=not confirm_overwrite and os.path.exists(DATASET_PATH))

    if not os.path.exists(DATASET_PATH) or regenerate:
        with st.spinner(f"Generating calibrated synthetic crowd dataset ({n_per_class * 3} samples)..."):
            df = generate_dataset(n_per_class=n_per_class, output_path=DATASET_PATH)
            st.success("Dataset successfully generated and saved to disk!")
    else:
        try:
            df = load_dataset(DATASET_PATH)
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return

    # ── High Level Overview Cards ────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Total Samples", f"{len(df):,}", "#636ee6"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Feature Count", f"{len(FEATURE_COLUMNS)}", "#a29bfe"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card_html("Classes", f"{len(LABEL_CLASSES)}", "#00b894"), unsafe_allow_html=True)
    with c4:
        missing_count = int(df.isnull().sum().sum())
        st.markdown(metric_card_html("Missing Values", f"{missing_count}", "#ffeaa7"), unsafe_allow_html=True)

    # ── Dataset Table & Download ─────────────────────────────────────
    st.markdown("---")
    st.subheader("Raw Data Preview", icon=":material/table_chart:")
    st.dataframe(df.head(100), width="stretch", height=300)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Dataset as CSV",
        icon=":material/download:",
        data=csv_bytes,
        file_name="crowd_dataset.csv",
        mime="text/csv",
    )

    # ── Class Distribution & Correlation ─────────────────────────────
    st.markdown("---")
    col_d1, col_d2 = st.columns([1, 1])

    with col_d1:
        st.subheader("Class Balance", icon=":material/balance:")
        class_counts = df["density_label"].value_counts().to_dict()
        fig_class = class_distribution_bar(class_counts)
        st.plotly_chart(fig_class, width="stretch")

    with col_d2:
        st.subheader("Feature Correlation Matrix", icon=":material/hub:")
        fig_corr = feature_correlation_heatmap(df, FEATURE_COLUMNS)
        st.plotly_chart(fig_corr, width="stretch")

    # ── Interactive Feature Analysis ─────────────────────────────────
    st.markdown("---")
    st.subheader("Interactive Feature Distribution Analysis", icon=":material/stacked_line_chart:")

    col_h1, col_h2 = st.columns([1, 1])

    with col_h1:
        st.markdown("##### Histogram by Class")
        selected_feat = st.selectbox(
            "Select Feature for Histogram",
            FEATURE_COLUMNS,
            index=0,
            key="hist_feat",
        )
        fig_hist = feature_distribution_histogram(df, selected_feat)
        st.plotly_chart(fig_hist, width="stretch")

    with col_h2:
        st.markdown("##### Feature Scatter Relationship")
        col_x, col_y = st.columns(2)
        with col_x:
            feat_x = st.selectbox("X Axis", FEATURE_COLUMNS, index=0, key="scatter_x")
        with col_y:
            feat_y = st.selectbox("Y Axis", FEATURE_COLUMNS, index=1, key="scatter_y")

        fig_scat = scatter_feature_vs_density(df, feat_x, feat_y)
        st.plotly_chart(fig_scat, width="stretch")

    # ── Summary Statistics Table ─────────────────────────────────────
    st.markdown("---")
    with st.expander("Numerical Descriptive Statistics (Mean, Std, Min, Max)", icon=":material/analytics:"):
        st.dataframe(df[FEATURE_COLUMNS].describe().T.style.format("{:.4f}"), width="stretch")
