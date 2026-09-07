"""
Reusable Metric Components for Visionlytics Dashboard.

Provides functions to display formatted metrics, stat cards,
and density indicators in the Streamlit UI.
"""

import streamlit as st
from app.components.styles import (
    metric_card_html,
    density_badge_html,
    DENSITY_COLORS,
)


def render_metric_row(metrics: dict):
    """
    Render a row of metric cards.

    Args:
        metrics: Dictionary mapping label → (value, color).
                 Example: {"People": ("14", "#00b894")}
    """
    cols = st.columns(len(metrics))
    for col, (label, (value, color)) in zip(cols, metrics.items()):
        with col:
            st.markdown(metric_card_html(label, value, color), unsafe_allow_html=True)


def render_density_badge(density: str):
    """Render a colored density badge."""
    st.markdown(density_badge_html(density), unsafe_allow_html=True)


def render_stats_table(stats: dict):
    """
    Render a formatted statistics table.

    Args:
        stats: Dictionary mapping stat name → value.
    """
    rows = ""
    for name, value in stats.items():
        rows += f"<tr><td>{name}</td><td>{value}</td></tr>"

    html = f"""
    <div class="section-container">
        <table class="stats-table">
            {rows}
        </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_analysis_metrics(features: dict, density: str, confidence: float):
    """
    Render the complete analysis metrics panel.

    Args:
        features: Extracted feature dictionary.
        density: Predicted density label.
        confidence: Model confidence score (0-1).
    """
    density_color = DENSITY_COLORS.get(density, "#ffffff")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            metric_card_html("People Detected", str(int(features['people_count'])), "#636ee6"),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            metric_card_html("Crowd Density", density, density_color),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            metric_card_html("Occupancy", f"{features['occupancy_ratio']*100:.1f}%", "#a29bfe"),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            metric_card_html("Confidence", f"{confidence*100:.1f}%", "#ffeaa7"),
            unsafe_allow_html=True,
        )
