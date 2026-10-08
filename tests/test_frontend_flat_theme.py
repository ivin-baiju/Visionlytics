"""
Frontend unit tests: flat-theme contract and container-safety guarantees.

These lock in the Wave 2/3/4 invariants:
  * the design system is flat (no glassmorphism, no gradients, no keyframes),
  * every public style/icon primitive still renders,
  * no UI module imports the backend package at import time, so the frontend
    container can start with only `frontend/` mounted.
"""

import importlib
import inspect

UI_MODULES = [
    "app.main",
    "app.ui.dashboard",
    "app.ui.image_analysis",
    "app.ui.video_analysis",
    "app.ui.live_camera",
    "app.ui.dataset_page",
    "app.ui.about",
    "app.ui.ml_models",
    "app.components.metrics",
    "app.components.theme",
    "app.components.charts",
    "app.components.icons",
    "app.components.styles",
    "app.api_client",
]


# ── Flat design contract ─────────────────────────────────────────────────────

def test_css_has_no_glassmorphism_remnants():
    styles = importlib.import_module("app.components.styles")
    css = styles.get_custom_css()

    forbidden = (
        "backdrop-filter",
        "linear-gradient",
        "radial-gradient",
        "blur(",
    )
    found = [token for token in forbidden if token in css]
    assert not found, f"glassmorphism remnants in CSS: {found}"

    # Only the sanctioned Mono-Clay motion set may use keyframes.
    keyframe_names = [
        line.split("@keyframes", 1)[1].split("{")[0].strip()
        for line in css.splitlines()
        if "@keyframes" in line
    ]
    assert keyframe_names, "expected sanctioned clay keyframes"
    assert set(keyframe_names) <= {"clay-rise", "clay-pulse"}, (
        f"unsanctioned keyframes: {keyframe_names}"
    )


def test_css_uses_clay_tokens():
    styles = importlib.import_module("app.components.styles")
    css = styles.get_custom_css()

    for token in ("#E9EBF0", "#FFFFFF", "#14161A", "#4F46E5"):
        assert token in css, f"missing mono-clay token {token}"

    # Embossed clay surfaces: both raised and pressed shadow directions.
    assert "8px 8px 16px rgba(15, 23, 42" in css
    assert "inset 4px 4px 8px rgba(15, 23, 42" in css
    # Tactile press states and motion-safety handling.
    assert ":active" in css
    assert "prefers-reduced-motion" in css


def test_theme_density_tokens_are_consistent():
    theme = importlib.import_module("app.components.theme")
    styles = importlib.import_module("app.components.styles")

    # styles re-exports the theme dictionaries.
    assert styles.DENSITY_COLORS == theme.DENSITY
    assert styles.DENSITY_BG_COLORS == theme.DENSITY_BG
    assert set(theme.DENSITY) == {"LOW", "MEDIUM", "HIGH"}
    assert set(theme.DENSITY_BG) == {"LOW", "MEDIUM", "HIGH"}


def test_chart_palette_is_mono_clay():
    charts = importlib.import_module("app.components.charts")

    assert charts.GRID_COLOR == "#E5E7EB"
    assert charts.BG_COLOR == "#FFFFFF"
    assert set(charts.DENSITY_COLORS_MAP) == {"LOW", "MEDIUM", "HIGH"}
    assert charts.DENSITY_COLORS_MAP == {
        "LOW": "#9CA3AF",
        "MEDIUM": "#4B5563",
        "HIGH": "#14161A",
    }
    assert "rgba(74, 125, 255" not in repr(charts.ACCENT_COLORS)



# ── Primitive rendering ──────────────────────────────────────────────────────

def test_style_primitives_render():
    styles = importlib.import_module("app.components.styles")

    assert "hero-section" in styles.header_html()
    assert "density-badge density-low" in styles.density_badge_html("LOW")
    assert "density-badge density-high" in styles.density_badge_html("HIGH")
    assert "metric-card" in styles.metric_card_html("Label", "1")
    assert "status-card" in styles.status_card_html("API", "up", True)
    assert "feature-card" in styles.feature_card_html("<svg/>", "Title", "Desc")
    assert "arch-card" in styles.arch_card_html("<svg/>", "Title", ["item"])
    assert "clay-banner" in styles.offline_banner_html("Backend unreachable")


def test_icons_are_flat_and_inherit_color():
    icons = importlib.import_module("app.components.icons")

    assert "linearGradient" not in icons.BRAND_LOGO_SVG
    assert "radialGradient" not in icons.BRAND_LOGO_SVG
    assert "currentColor" in icons.BRAND_LOGO_SVG

    for name in (
        "ICON_IMAGE_ANALYSIS",
        "ICON_VIDEO_ANALYSIS",
        "ICON_LIVE_CAMERA",
        "ICON_COMPUTER_VISION",
        "ICON_FEATURE_ENGINEERING",
        "ICON_MACHINE_LEARNING",
        "ICON_TARGET",
        "ICON_OBJECTIVES",
    ):
        svg = getattr(icons, name)
        assert "currentColor" in svg, f"{name} does not inherit currentColor"
        assert "linearGradient" not in svg, f"{name} still uses a gradient"


def test_page_header_primitive():
    theme = importlib.import_module("app.components.theme")

    html = theme.page_header_html("Title", "Subtitle")
    assert "page-tick" in html
    assert "Title" in html
    assert "Subtitle" in html
    assert "page-subtitle" not in theme.page_header_html("OnlyTitle")


# ── Container safety ─────────────────────────────────────────────────────────

def test_frontend_modules_do_not_import_backend_at_module_level():
    """No UI module may hard-import the backend package at import time."""
    backend_roots = ("machine_learning", "computer_vision", "dataset.", "dataset import", "db.")

    for module_name in UI_MODULES:
        module = importlib.import_module(module_name)
        source = inspect.getsource(module)

        for line in source.splitlines():
            # Module-level means column 0 — indented lines are lazy imports
            # inside functions, which are exactly the guarded pattern we want.
            if line[:1].isspace() or not line.strip():
                continue
            stripped = line.strip()
            if not (stripped.startswith("from ") or stripped.startswith("import ")):
                continue
            for root in backend_roots:
                assert not stripped.startswith(f"from {root}"), (
                    f"{module_name} has a module-level import of {root}: {stripped}"
                )
                assert not stripped.startswith(f"import {root}"), (
                    f"{module_name} has a module-level import of {root}: {stripped}"
                )


def test_no_legacy_frontend_package_imports():
    """`from frontend.app...` breaks the Docker layout; only `app.*` is allowed."""
    for module_name in UI_MODULES:
        module = importlib.import_module(module_name)
        source = inspect.getsource(module)
        assert "from frontend.app" not in source, module_name
        assert "import frontend.app" not in source, module_name


def test_api_client_surface():
    api_client = importlib.import_module("app.api_client")

    for fn_name in (
        "analyze_frame_api",
        "check_api_health",
        "get_dataset_info_api",
        "get_dataset_preview_api",
        "generate_dataset_api",
        "get_models_list_api",
        "get_model_evaluation_api",
        "get_feature_importance_api",
        "train_models_api",
    ):
        assert callable(getattr(api_client, fn_name)), fn_name


def test_api_client_returns_none_when_backend_unreachable(monkeypatch):
    api_client = importlib.import_module("app.api_client")
    monkeypatch.setattr(api_client, "API_URL", "http://127.0.0.1:9", raising=False)

    assert api_client.get_dataset_info_api() is None
    assert api_client.get_models_list_api() is None
    assert api_client.check_api_health() is False


def test_analyze_frame_api_exposes_optional_controls():
    """The UI settings (confidence / tracking / attributes) must be sendable."""
    api_client = importlib.import_module("app.api_client")

    params = inspect.signature(api_client.analyze_frame_api).parameters
    for name in ("confidence", "track", "attributes"):
        assert name in params, name


# ── Page wiring ──────────────────────────────────────────────────────────────

def test_video_page_caches_results_instead_of_reprocessing():
    video = importlib.import_module("app.ui.video_analysis")

    assert callable(video._process_video)
    assert callable(video._render_video_results)

    render_source = inspect.getsource(video.render_video_analysis)
    # Results come from the session cache; a re-run must not re-process frames.
    assert "video_analysis_cache" in render_source
    assert "_process_video(" in render_source
    assert "_render_video_results(" in render_source

    process_source = inspect.getsource(video._process_video)
    assert "confidence=min_confidence" in process_source
    assert "track=enable_tracking" in process_source


def test_image_page_wires_confidence_and_attributes():
    image_mod = importlib.import_module("app.ui.image_analysis")
    source = inspect.getsource(image_mod.render_image_analysis)

    assert "confidence=min_confidence" in source
    assert "attributes=enable_attributes" in source
    assert 'api_response.get("attributes"' in source
    # The slider value must be bound to a name, otherwise it is a dead control.
    assert "min_confidence = st.slider(" in source

