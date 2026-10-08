"""
Frontend wiring tests: control→backend plumbing and rerun-safety.

These lock in the behaviours that were silently broken before:
  * page controls (confidence, tracking, attributes) actually reach the API,
  * read-only API responses are cached across Streamlit reruns,
  * pages do not re-run inference / reprocess videos on every interaction.
"""

import importlib
import inspect
import sys
import types


def _fake_streamlit(session_state: dict) -> types.ModuleType:
    """Minimal stand-in for `streamlit` exposing only session_state."""
    module = types.ModuleType("streamlit")
    module.session_state = session_state
    return module


# ── Read-through API cache ───────────────────────────────────────────────────

def test_read_only_endpoints_are_cached_across_reruns(monkeypatch):
    api_client = importlib.import_module("app.api_client")
    calls = {"n": 0}

    def fake_get(path, params=None, timeout=15.0):
        calls["n"] += 1
        return {"value": calls["n"], "path": path}

    monkeypatch.setattr(api_client, "_get_json", fake_get)
    monkeypatch.setitem(sys.modules, "streamlit", _fake_streamlit({}))

    first = api_client.get_dataset_info_api()
    second = api_client.get_dataset_info_api()

    assert first == second, "second call should be served from cache"
    assert calls["n"] == 1

    # Different params are cached separately.
    api_client.get_dataset_preview_api(limit=10)
    api_client.get_dataset_preview_api(limit=10)
    api_client.get_dataset_preview_api(limit=20)
    assert calls["n"] == 3


def test_clear_api_cache_drops_entries(monkeypatch):
    api_client = importlib.import_module("app.api_client")
    calls = {"n": 0}

    def fake_get(path, params=None, timeout=15.0):
        calls["n"] += 1
        return {"value": calls["n"]}

    state: dict = {}
    monkeypatch.setattr(api_client, "_get_json", fake_get)
    monkeypatch.setitem(sys.modules, "streamlit", _fake_streamlit(state))

    api_client.get_models_list_api()
    api_client.get_models_list_api()
    assert calls["n"] == 1
    assert state, "expected a cached entry"

    api_client.clear_api_cache()
    assert state == {}, "clear_api_cache must remove cached entries"

    api_client.get_models_list_api()
    assert calls["n"] == 2


def test_mutating_endpoints_invalidate_the_cache(monkeypatch):
    api_client = importlib.import_module("app.api_client")

    cleared = {"n": 0}
    monkeypatch.setattr(api_client, "clear_api_cache", lambda: cleared.__setitem__("n", cleared["n"] + 1))
    monkeypatch.setattr(api_client, "_post_json", lambda path, params=None, timeout=600.0: {"ok": True})

    assert api_client.train_models_api() == {"ok": True}
    assert api_client.generate_dataset_api(n_per_class=500) == {"ok": True}
    assert cleared["n"] == 2


def test_health_probe_is_memoised(monkeypatch):
    api_client = importlib.import_module("app.api_client")

    probes = {"n": 0}
    monkeypatch.setattr(
        api_client,
        "check_api_health",
        lambda: (probes.__setitem__("n", probes["n"] + 1) or True),
    )
    monkeypatch.setitem(sys.modules, "streamlit", _fake_streamlit({}))

    assert api_client.check_api_health_cached() is True
    assert api_client.check_api_health_cached() is True
    assert probes["n"] == 1, "second probe within the TTL must be cached"


# ── Page wiring ──────────────────────────────────────────────────────────────

def test_live_camera_wires_its_controls():
    live = importlib.import_module("app.ui.live_camera")
    source = inspect.getsource(live.render_live_camera)

    assert "min_confidence = st.slider(" in source
    assert "enable_tracking = st.toggle(" in source
    assert "confidence=min_confidence" in source
    assert "track=enable_tracking" in source
    assert "_draw_track_ids(" in source
    # The old cadence saved on every frame during even seconds.
    assert "int(curr_time) % 2" not in source
    assert "DB_SAVE_EVERY" in source


def test_image_page_caches_inference_response():
    image_mod = importlib.import_module("app.ui.image_analysis")
    source = inspect.getsource(image_mod.render_image_analysis)

    assert "image_analysis_cache" in source
    # Inference must only run on cache miss.
    assert "cached_analysis[\"key\"] == analysis_key" in source
    # The old placeholder meant the Visual Attributes view was always empty.
    assert "attributes_list = []" not in source


def test_dashboard_reports_live_system_status():
    dashboard = importlib.import_module("app.ui.dashboard")
    source = inspect.getsource(dashboard.render_dashboard)

    assert "check_api_health_cached()" in source
    assert "get_models_list_api()" in source
    # Status cards must not claim health unconditionally any more.
    assert 'status_card_html("ML Classifiers", "7 Loaded")' not in source
    assert 'status_card_html("Core Backend", "Online")' not in source


def test_dataset_page_tolerates_missing_columns():
    dataset = importlib.import_module("app.ui.dataset_page")
    source = inspect.getsource(dataset.render_dataset_page)

    assert "available_features" in source
    assert 'if "density_label" in df.columns' in source or 'has_labels = "density_label" in df.columns' in source
