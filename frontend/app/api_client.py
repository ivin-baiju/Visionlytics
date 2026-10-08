import requests
import cv2
import numpy as np

import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")


def _get_json(path: str, params: dict | None = None, timeout: float = 15.0):
    """GET helper returning parsed JSON, or None on any failure."""
    try:
        response = requests.get(f"{API_URL}{path}", params=params, timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None


def _post_json(path: str, params: dict | None = None, timeout: float = 600.0):
    """POST helper returning parsed JSON, or None on any failure."""
    try:
        response = requests.post(f"{API_URL}{path}", params=params, timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None


def check_api_health() -> bool:
    """Return True when the FastAPI backend responds to /health."""
    try:
        return requests.get(f"{API_URL}/health", timeout=2).status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_api_health_cached(ttl: float = 30.0) -> bool:
    """Cached health probe honouring the ``_api_health_cache`` session key.

    ``main.py`` clears ``st.session_state["_api_health_cache"]`` on
    "Re-check connection", so this helper stores ``(result, timestamp)``
    there instead of ``st.cache_data`` (which that pop could not clear).
    Falls back to a direct probe when called outside a Streamlit session.
    """
    import time

    try:
        import streamlit as st

        now = time.time()
        cached = st.session_state.get("_api_health_cache")
        if cached is not None:
            result, ts = cached
            if now - float(ts) < ttl:
                return bool(result)
        result = check_api_health()
        st.session_state["_api_health_cache"] = (result, now)
        return result
    except Exception:
        return check_api_health()


def clear_api_cache() -> None:
    """Clear all cached read-only API endpoint responses from session state."""
    try:
        import streamlit as st

        keys = [k for k in list(st.session_state.keys()) if k.startswith("_api_cache_")]
        for k in keys:
            del st.session_state[k]
    except Exception:
        pass


def _cached_get(path: str, params: dict | None = None, timeout: float = 15.0):
    """GET helper that caches results in st.session_state across reruns."""
    try:
        import streamlit as st

        param_items = tuple(sorted(params.items())) if params else ()
        cache_key = f"_api_cache_{path}_{param_items}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        result = _get_json(path, params=params, timeout=timeout)
        if result is not None:
            st.session_state[cache_key] = result
        return result
    except Exception:
        return _get_json(path, params=params, timeout=timeout)


def analyze_frame_api(
    frame: np.ndarray,
    confidence: float | None = None,
    track: bool = False,
    attributes: bool = False,
):
    """Send a frame to the FastAPI backend for analysis."""
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()

    params = {}
    if confidence is not None:
        params["confidence"] = confidence
    if track:
        params["track"] = True
    if attributes:
        params["attributes"] = True

    try:
        response = requests.post(
            f"{API_URL}/analyze/frame",
            params=params or None,
            files={"file": ("frame.jpg", img_bytes, "image/jpeg")},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        # Surface non-200s in the Streamlit log so pages that show a generic
        # "API offline" message don't mask backend errors (e.g. a 500).
        print(
            f"[api_client] POST /analyze/frame -> HTTP {response.status_code}: "
            f"{response.text[:300]}"
        )
    except requests.exceptions.RequestException as exc:
        print(f"[api_client] POST /analyze/frame failed: {exc}")

    return None


# ── Dataset endpoints ────────────────────────────────────────────────────────

def get_dataset_info_api():
    """Lightweight dataset metadata (no rows)."""
    return _cached_get("/dataset/info")


def get_dataset_preview_api(limit: int = 3000):
    """Dataset rows (capped server-side) plus class counts and column names."""
    return _cached_get("/dataset/preview", params={"limit": limit})


def generate_dataset_api(n_per_class: int = 500):
    """Regenerate the synthetic dataset server-side; returns a fresh preview."""
    clear_api_cache()
    return _post_json("/dataset/generate", params={"n_per_class": n_per_class})


# ── ML model registry endpoints ──────────────────────────────────────────────

def get_models_list_api():
    """Trained artifact inventory plus the champion model name."""
    return _cached_get("/models/list")


def get_model_evaluation_api():
    """Saved validation/test metrics for all trained models."""
    return _cached_get("/models/evaluation")


def get_feature_importance_api(model_name: str | None = None):
    """Feature importances for the champion (or a named) model."""
    params = {"model_name": model_name} if model_name else None
    return _cached_get("/models/feature-importance", params=params)


def train_models_api():
    """Trigger full retraining of all models server-side."""
    clear_api_cache()
    return _post_json("/models/train")

