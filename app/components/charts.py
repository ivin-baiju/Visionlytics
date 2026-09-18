"""
Chart Components for Visionlytics Dashboard.

Reusable Plotly chart builders for visualizing crowd analytics,
model performance, and dataset statistics. Uses a light, premium
color palette with clean white backgrounds and soft gradients.
"""


import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── Common Theme ─────────────────────────────────────────────────────────────

PLOTLY_TEMPLATE = "plotly_white"
BG_COLOR = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(74, 125, 255, 0.06)"
FONT_COLOR = "#3a4560"
DENSITY_COLORS_MAP = {"LOW": "#2ECDA7", "MEDIUM": "#FFB347", "HIGH": "#FF6B6B"}
ACCENT_COLORS = ["#4A7DFF", "#2ECDA7", "#FFB347", "#FF6B6B", "#A78BFA"]


def _base_layout(title: str = "", height: int = 400) -> dict:
    """Return common Plotly layout settings."""
    return {
        "template": PLOTLY_TEMPLATE,
        "paper_bgcolor": BG_COLOR,
        "plot_bgcolor": BG_COLOR,
        "font": {"family": "Inter", "color": FONT_COLOR},
        "title": {"text": title, "font": {"size": 16, "color": "#1a2340"}},
        "height": height,
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        "xaxis": {"gridcolor": GRID_COLOR, "zerolinecolor": GRID_COLOR},
        "yaxis": {"gridcolor": GRID_COLOR, "zerolinecolor": GRID_COLOR},
    }


# ── Crowd Analytics Charts ───────────────────────────────────────────────────

def density_distribution_pie(class_counts: dict[str, int]) -> go.Figure:
    """Pie chart showing crowd density class distribution."""
    labels = list(class_counts.keys())
    values = list(class_counts.values())
    colors = [DENSITY_COLORS_MAP.get(l, "#4A7DFF") for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker={"colors": colors, "line": {"color": "#ffffff", "width": 2}},
        textinfo="label+percent",
        textfont={"size": 13},
    )])
    fig.update_layout(**_base_layout("Density Distribution", 350))
    return fig


def density_over_time(timestamps: list[float], densities: list[str]) -> go.Figure:
    """Line chart showing crowd density changes over time."""
    density_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    density_nums = [density_map.get(d, 0) for d in densities]
    colors = [DENSITY_COLORS_MAP.get(d, "#4A7DFF") for d in densities]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=density_nums,
        mode="lines+markers",
        line={"color": "#4A7DFF", "width": 2},
        marker={"color": colors, "size": 6, "line": {"width": 1, "color": "#ffffff"}},
        hovertemplate="Time: %{x:.1f}s<br>Density: %{text}<extra></extra>",
        text=densities,
    ))

    layout = _base_layout("Crowd Density Over Time", 350)
    layout["yaxis"] = {
        "tickvals": [1, 2, 3],
        "ticktext": ["LOW", "MEDIUM", "HIGH"],
        "gridcolor": GRID_COLOR,
        "range": [0.5, 3.5],
    }
    layout["xaxis"]["title"] = "Time (seconds)"
    fig.update_layout(**layout)
    return fig


def people_count_over_time(timestamps: list[float], counts: list[int]) -> go.Figure:
    """Area chart showing people count over time."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=counts,
        fill="tozeroy",
        fillcolor="rgba(74, 125, 255, 0.12)",
        line={"color": "#4A7DFF", "width": 2},
        mode="lines",
    ))

    layout = _base_layout("People Count Over Time", 300)
    layout["xaxis"]["title"] = "Time (seconds)"
    layout["yaxis"]["title"] = "People Count"
    fig.update_layout(**layout)
    return fig


def region_distribution_bar(top: int, middle: int, bottom: int) -> go.Figure:
    """Bar chart showing people distribution across frame regions."""
    fig = go.Figure(data=[go.Bar(
        x=["Top", "Middle", "Bottom"],
        y=[top, middle, bottom],
        marker_color=["#4A7DFF", "#A78BFA", "#2ECDA7"],
        text=[top, middle, bottom],
        textposition="auto",
    )])

    layout = _base_layout("Regional Distribution", 300)
    layout["xaxis"]["title"] = "Frame Region"
    layout["yaxis"]["title"] = "Count"
    fig.update_layout(**layout)
    return fig


# ── Model Performance Charts ────────────────────────────────────────────────

def model_comparison_bar(comparison_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing model metrics."""
    fig = go.Figure()

    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    colors = ACCENT_COLORS[:len(metrics)]

    for i, metric in enumerate(metrics):
        if metric in comparison_df.columns:
            fig.add_trace(go.Bar(
                name=metric,
                x=comparison_df["Model"],
                y=comparison_df[metric],
                marker_color=colors[i],
                text=comparison_df[metric].apply(lambda x: f"{x:.3f}"),
                textposition="auto",
            ))

    layout = _base_layout("Model Performance Comparison", 420)
    layout["barmode"] = "group"
    layout["xaxis"]["title"] = "Model"
    layout["yaxis"]["title"] = "Score"
    layout["yaxis"]["range"] = [0, 1.05]
    layout["legend"] = {"orientation": "h", "y": 1.12, "x": 0.5, "xanchor": "center"}
    fig.update_layout(**layout)
    return fig


def confusion_matrix_heatmap(
    cm: list[list[int]],
    class_names: list[str],
    title: str = "Confusion Matrix",
) -> go.Figure:
    """Heatmap visualization of a confusion matrix."""
    cm_array = np.array(cm)

    total = cm_array.sum()
    annotations = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            count = cm_array[i][j]
            pct = (count / total * 100) if total > 0 else 0
            annotations.append(f"{count}<br>({pct:.1f}%)")

    annotations = np.array(annotations).reshape(len(class_names), len(class_names))

    fig = go.Figure(data=go.Heatmap(
        z=cm_array,
        x=class_names,
        y=class_names,
        text=annotations,
        texttemplate="%{text}",
        colorscale=[[0, "#eef3fb"], [0.5, "#6B9FFF"], [1, "#4A7DFF"]],
        showscale=False,
    ))

    layout = _base_layout(title, 350)
    layout["xaxis"]["title"] = "Predicted"
    layout["yaxis"]["title"] = "Actual"
    layout["yaxis"]["autorange"] = "reversed"
    fig.update_layout(**layout)
    return fig


def feature_importance_bar(
    feature_names: list[str],
    importances: list[float],
) -> go.Figure:
    """Horizontal bar chart of feature importances."""
    sorted_idx = np.argsort(importances)
    sorted_names = [feature_names[i] for i in sorted_idx]
    sorted_vals = [importances[i] for i in sorted_idx]

    fig = go.Figure(data=[go.Bar(
        x=sorted_vals,
        y=sorted_names,
        orientation="h",
        marker={
            "color": sorted_vals,
            "colorscale": [[0, "#eef3fb"], [1, "#4A7DFF"]],
        },
        text=[f"{v:.4f}" for v in sorted_vals],
        textposition="auto",
    )])

    layout = _base_layout("Feature Importance", 400)
    layout["xaxis"]["title"] = "Importance"
    fig.update_layout(**layout)
    return fig


def training_time_bar(training_times: dict[str, float]) -> go.Figure:
    """Bar chart comparing model training times."""
    names = list(training_times.keys())
    times = list(training_times.values())

    fig = go.Figure(data=[go.Bar(
        x=names,
        y=times,
        marker_color=ACCENT_COLORS[:len(names)],
        text=[f"{t:.3f}s" for t in times],
        textposition="auto",
    )])

    layout = _base_layout("Training Time Comparison", 300)
    layout["yaxis"]["title"] = "Time (seconds)"
    fig.update_layout(**layout)
    return fig


# ── Dataset Exploration Charts ───────────────────────────────────────────────

def feature_correlation_heatmap(df: pd.DataFrame, feature_cols: list[str]) -> go.Figure:
    """Heatmap of feature correlations."""
    corr = df[feature_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=[c.replace("_", " ").title()[:15] for c in corr.columns],
        y=[c.replace("_", " ").title()[:15] for c in corr.index],
        colorscale=[[0, "#FF6B6B"], [0.5, "#f8faff"], [1, "#2ECDA7"]],
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont={"size": 9},
    ))

    layout = _base_layout("Feature Correlation Matrix", 500)
    fig.update_layout(**layout)
    return fig


def feature_distribution_histogram(
    df: pd.DataFrame,
    feature: str,
    label_col: str = "density_label",
) -> go.Figure:
    """Histogram of a feature, colored by density class."""
    fig = go.Figure()

    for label, color in DENSITY_COLORS_MAP.items():
        subset = df[df[label_col] == label]
        if len(subset) > 0:
            fig.add_trace(go.Histogram(
                x=subset[feature],
                name=label,
                marker_color=color,
                opacity=0.7,
            ))

    title = feature.replace("_", " ").title()
    layout = _base_layout(f"Distribution: {title}", 350)
    layout["barmode"] = "overlay"
    layout["xaxis"]["title"] = title
    layout["yaxis"]["title"] = "Count"
    layout["legend"] = {"orientation": "h", "y": 1.12, "x": 0.5, "xanchor": "center"}
    fig.update_layout(**layout)
    return fig


def class_distribution_bar(class_counts: dict[str, int]) -> go.Figure:
    """Bar chart of class label distribution in the dataset."""
    labels = list(class_counts.keys())
    counts = list(class_counts.values())
    colors = [DENSITY_COLORS_MAP.get(l, "#4A7DFF") for l in labels]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=counts,
        marker_color=colors,
        text=counts,
        textposition="auto",
    )])

    layout = _base_layout("Class Distribution", 300)
    layout["xaxis"]["title"] = "Density Class"
    layout["yaxis"]["title"] = "Count"
    fig.update_layout(**layout)
    return fig


def scatter_feature_vs_density(
    df: pd.DataFrame,
    feature_x: str,
    feature_y: str,
    label_col: str = "density_label",
) -> go.Figure:
    """Scatter plot of two features, colored by density class."""
    fig = go.Figure()

    for label, color in DENSITY_COLORS_MAP.items():
        subset = df[df[label_col] == label]
        if len(subset) > 0:
            fig.add_trace(go.Scatter(
                x=subset[feature_x],
                y=subset[feature_y],
                mode="markers",
                name=label,
                marker={"color": color, "size": 5, "opacity": 0.6},
            ))

    x_title = feature_x.replace("_", " ").title()
    y_title = feature_y.replace("_", " ").title()
    layout = _base_layout(f"{x_title} vs {y_title}", 400)
    layout["xaxis"]["title"] = x_title
    layout["yaxis"]["title"] = y_title
    layout["legend"] = {"orientation": "h", "y": 1.12, "x": 0.5, "xanchor": "center"}
    fig.update_layout(**layout)
    return fig


def attribute_bar_chart(attribute_counts: dict[str, int], title: str) -> go.Figure:
    """Bar chart of visual attribute distribution (hair color, clothing color)."""
    labels = list(attribute_counts.keys())
    counts = list(attribute_counts.values())

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=counts,
        marker_color=ACCENT_COLORS[:len(labels)] if len(labels) <= len(ACCENT_COLORS)
                     else ["#4A7DFF"] * len(labels),
        text=counts,
        textposition="auto",
    )])

    layout = _base_layout(title, 300)
    fig.update_layout(**layout)
    return fig
