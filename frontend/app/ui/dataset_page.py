"""
Dataset Exploration Page for Visionlytics.

Provides interactive dataset exploration, descriptive statistics,
class distributions, feature correlation heatmaps, distribution histograms,
and dataset regeneration controls.
"""

import os

import pandas as pd
import streamlit as st

from app.api_client import get_dataset_info_api, get_dataset_preview_api
from app.components.charts import (
    class_distribution_bar,
    feature_correlation_heatmap,
    feature_distribution_histogram,
    scatter_feature_vs_density,
)
from app.components.styles import header_html, metric_card_html
from app.components.theme import INK, MUTED

# Fallbacks so the page still renders if the backend is unreachable.
FALLBACK_FEATURE_COLUMNS = [
    "people_count",
    "occupancy_ratio",
    "avg_person_area",
    "avg_distance",
    "min_distance",
    "spatial_spread",
    "top_region_count",
    "middle_region_count",
    "bottom_region_count",
    "frame_occupancy_density",
]
FALLBACK_LABEL_CLASSES = ["LOW", "MEDIUM", "HIGH"]


def _local_dataset_fallback():
    """Best-effort local dataset load for offline/dev runs.

    Returns a DataFrame or None. The backend package is not shipped inside the
    frontend container, so this import is attempted lazily and never fatal.
    """
    try:
        from machine_learning.preprocessing import (  # noqa: PLC0415
            DATASET_PATH,
            load_dataset,
        )

        if not os.path.exists(DATASET_PATH):
            return None
        return load_dataset(DATASET_PATH)
    except Exception:
        return None


def render_dataset_page():
    """Render the Dataset Exploration page."""
    st.html(header_html())
    st.header("Dataset exploration & analytics", icon=":material/dataset:")

    st.markdown(
        "Inspect the training dataset, examine feature distributions, "
        "verify class balance, and study spatial correlation patterns."
    )

    # ── Backend dataset metadata (drives columns/labels) ─────────────
    info = get_dataset_info_api() or {}
    feature_columns = info.get("feature_columns") or FALLBACK_FEATURE_COLUMNS
    label_classes = info.get("class_labels") or FALLBACK_LABEL_CLASSES

    backend_online = bool(info)
    dataset_exists = bool(info.get("exists", False))

    if not backend_online:
        st.warning(
            "Backend API is offline — falling back to a direct local dataset read. "
            "Start the FastAPI service for full functionality.",
            icon=":material/cloud_off:",
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
            st.write("")  # Spacer
            st.write("")  # Spacer
            regenerate = st.button(
                "Regenerate Dataset",
                icon=":material/refresh:",
                type="primary" if confirm_overwrite else "secondary",
                disabled=not confirm_overwrite and dataset_exists,
            )

    # ── Load dataset via API, with generate/fallback paths ───────────
    df = None
    source_label = ""

    if regenerate:
        with st.spinner(f"Generating calibrated synthetic crowd dataset ({n_per_class * 3} samples)..."):
            from app.api_client import generate_dataset_api  # noqa: PLC0415

            payload = generate_dataset_api(n_per_class=int(n_per_class))
        if payload:
            df = pd.DataFrame(payload["rows"], columns=payload["columns"])
            st.success(
                f"Dataset regenerated server-side: {payload.get('n_rows', len(df)):,} samples."
            )
            source_label = "Backend API"
        else:
            st.error("Regeneration failed — the backend API did not respond.")
            return
    else:
        payload = get_dataset_preview_api()
        if payload:
            df = pd.DataFrame(payload["rows"], columns=payload["columns"])
            source_label = "Backend API"
        else:
            df = _local_dataset_fallback()
            source_label = "Local disk"

    if df is None or len(df) == 0:
        st.error(
            "No dataset available. Ensure the FastAPI backend is running, "
            "then use **Regenerate Dataset** above.",
            icon=":material/database_off:",
        )
        return

    st.caption(f"Data source: **{source_label}** · {len(df):,} rows loaded")


    available_features = [c for c in feature_columns if c in df.columns]

    # ── High Level Overview Cards ────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Total Samples", f"{len(df):,}", INK), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Feature Count", f"{len(available_features)}", MUTED), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card_html("Classes", f"{len(label_classes)}", INK), unsafe_allow_html=True)
    with c4:
        missing_count = int(df.isnull().sum().sum())
        st.markdown(metric_card_html("Missing Values", f"{missing_count}", MUTED), unsafe_allow_html=True)

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
        if "density_label" in df.columns:
            st.subheader("Class Balance", icon=":material/balance:")
            class_counts = df["density_label"].value_counts().to_dict()
            fig_class = class_distribution_bar(class_counts)
            st.plotly_chart(fig_class, width="stretch")
        else:
            st.info("Class label column 'density_label' not present in dataset.")

    with col_d2:
        if available_features:
            st.subheader("Feature Correlation Matrix", icon=":material/hub:")
            fig_corr = feature_correlation_heatmap(df, available_features)
            st.plotly_chart(fig_corr, width="stretch")

    # ── Interactive Feature Analysis ─────────────────────────────────
    if available_features:
        st.markdown("---")
        st.subheader("Interactive Feature Distribution Analysis", icon=":material/stacked_line_chart:")

        col_h1, col_h2 = st.columns([1, 1])

        with col_h1:
            st.markdown("##### Histogram by Class")
            selected_feat = st.selectbox(
                "Select Feature for Histogram",
                available_features,
                index=0,
                key="hist_feat",
            )
            fig_hist = feature_distribution_histogram(df, selected_feat)
            st.plotly_chart(fig_hist, width="stretch")

        with col_h2:
            st.markdown("##### Feature Scatter Relationship")
            col_x, col_y = st.columns(2)
            with col_x:
                feat_x = st.selectbox("X Axis", available_features, index=0, key="scatter_x")
            with col_y:
                feat_y = st.selectbox("Y Axis", available_features, index=min(1, len(available_features) - 1), key="scatter_y")

            fig_scat = scatter_feature_vs_density(df, feat_x, feat_y)
            st.plotly_chart(fig_scat, width="stretch")

        # ── Summary Statistics Table ─────────────────────────────────────
        st.markdown("---")
        with st.expander("Numerical Descriptive Statistics (Mean, Std, Min, Max)", icon=":material/analytics:"):
            st.dataframe(df[available_features].describe().T.style.format("{:.4f}"), width="stretch")

