"""Streamlit AppTest smoke tests: the app boots and renders without exceptions."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

FRONTEND_MAIN = Path(__file__).resolve().parent.parent / "frontend" / "app" / "main.py"


def test_app_boots_without_exceptions():
    """Run the real Streamlit script and assert no unhandled exception."""
    at = AppTest.from_file(str(FRONTEND_MAIN), default_timeout=60).run()

    assert not at.exception, f"app raised: {at.exception}"

    # The white-rail sidebar renders its brand block and navigation radio.
    # The brand block and navigation radio render cleanly.
    assert len(at.radio) >= 1 or len(at.sidebar.radio) >= 1, "navigation radio missing"
    assert len(at.markdown) >= 1 or len(at.sidebar.markdown) >= 1, "brand block missing"


def test_dashboard_renders_analyses_filter_panel():
    """Selecting the Dashboard page must render the Wave 3 filter controls."""
    at = AppTest.from_file(str(FRONTEND_MAIN), default_timeout=60).run()

    assert not at.exception, f"app raised: {at.exception}"

    nav = at.radio[0] if len(at.radio) >= 1 else at.sidebar.radio[0]
    assert nav.label == "Navigation"
    assert nav.options, "no navigation entries found"

    # Navigate explicitly to Dashboard and re-run.
    nav.set_value(nav.options[0])
    at.run()
    assert not at.exception, f"dashboard raised: {at.exception}"

    # Zone 2 of the dashboard exposes exactly two segmented controls
    # (Status + Source) for filtering the analyses list.
    assert len(at.segmented_control) == 2, (
        f"expected 2 analyses filter controls, found {len(at.segmented_control)}"
    )


@pytest.mark.slow
def test_every_page_route_renders():
    """Walk every entry and assert none of them raise."""
    # Discover the routes once, from a single instance.
    probe = AppTest.from_file(str(FRONTEND_MAIN), default_timeout=90).run()
    assert not probe.exception, f"app raised: {probe.exception}"
    nav_widget = probe.radio[0] if len(probe.radio) >= 1 else probe.sidebar.radio[0]
    options = list(nav_widget.options)
    assert options, "no navigation entries found"

    for option in options:
        at = AppTest.from_file(str(FRONTEND_MAIN), default_timeout=90).run()
        nav = at.radio[0] if len(at.radio) >= 1 else at.sidebar.radio[0]
        nav.set_value(option).run()
        assert not at.exception, f"page '{option}' raised: {at.exception}"


@pytest.mark.parametrize("page", ["dashboard", "about"])
def test_direct_module_import_of_pages(page):
    """Each page module must be importable in isolation."""
    import importlib

    module = importlib.import_module(f"app.ui.{page}")
    fn_name = "render_dashboard" if page == "dashboard" else "render_about"
    assert hasattr(module, fn_name)
