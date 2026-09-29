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


def analyze_frame_api(frame: np.ndarray):
    """Send a frame to the FastAPI backend for analysis."""
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()

    try:
        response = requests.post(
            f"{API_URL}/analyze/frame",
            files={"file": ("frame.jpg", img_bytes, "image/jpeg")},
            timeout=30
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
    return _get_json("/dataset/info")


def get_dataset_preview_api(limit: int = 3000):
    """Dataset rows (capped server-side) plus class counts and column names."""
    return _get_json("/dataset/preview", params={"limit": limit})


def generate_dataset_api(n_per_class: int = 500):
    """Regenerate the synthetic dataset server-side; returns a fresh preview."""
    return _post_json("/dataset/generate", params={"n_per_class": n_per_class})


# ── ML model registry endpoints ──────────────────────────────────────────────

def get_models_list_api():
    """Trained artifact inventory plus the champion model name."""
    return _get_json("/models/list")


def get_model_evaluation_api():
    """Saved validation/test metrics for all trained models."""
    return _get_json("/models/evaluation")


def get_feature_importance_api(model_name: str | None = None):
    """Feature importances for the champion (or a named) model."""
    params = {"model_name": model_name} if model_name else None
    return _get_json("/models/feature-importance", params=params)


def train_models_api():
    """Trigger full retraining of all 7 models server-side."""
    return _post_json("/models/train")
