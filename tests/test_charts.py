"""
Chart component tests.

Locks in the fix for the Dashboard crash where a ``range`` object was passed
as Plotly series data (Plotly only accepts tuple/list/numpy/pandas arrays).
"""

import importlib


def test_people_count_over_time_accepts_range_inputs():
    """Plotly rejects bare ``range`` objects — the chart builder must coerce."""
    charts = importlib.import_module("app.components.charts")

    counts = [3, 1, 4]
    fig = charts.people_count_over_time(range(len(counts)), counts)

    trace = fig.data[0]
    assert list(trace.x) == [0, 1, 2]
    assert list(trace.y) == [3, 1, 4]


def test_people_count_over_time_accepts_common_iterables():
    charts = importlib.import_module("app.components.charts")

    import numpy as np
    import pandas as pd

    fig = charts.people_count_over_time(
        pd.Series([0.0, 0.5, 1.0]),
        np.array([2, 5, 1]),
    )

    trace = fig.data[0]
    assert list(trace.x) == [0.0, 0.5, 1.0]
    assert list(trace.y) == [2, 5, 1]


def test_dashboard_chart_call_sites_use_lists():
    """The dashboard must not pass a raw ``range`` into chart builders."""
    import inspect

    dashboard = importlib.import_module("app.ui.dashboard")
    source = inspect.getsource(dashboard)

    # The buggy pattern passed `range(len(df))` directly as chart data.
    assert "range(len(df))" not in source
    # Fixed pattern wraps the index in list() and passes counts as y.
    assert "list(range(len(counts)))" in source
