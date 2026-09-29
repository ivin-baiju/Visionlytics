"""
Integration tests for the Visionlytics FastAPI backend.

Covers the health probe, frame analysis, and the dataset / model-registry
endpoints added in Wave 4. Uses FastAPI's TestClient so no live server or
network access is required.
"""

import importlib

import numpy as np
import pytest

fastapi_app = importlib.import_module("main").app


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    with TestClient(fastapi_app) as test_client:
        yield test_client


# ── Health ───────────────────────────────────────────────────────────────────

def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Frame analysis ───────────────────────────────────────────────────────────

def _jpeg_bytes(height=200, width=200):
    import cv2

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", frame)
    assert ok
    return encoded.tobytes()


def test_analyze_frame_contract(client):
    response = client.post(
        "/analyze/frame",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200

    payload = response.json()
    for key in (
        "density_label",
        "confidence",
        "probabilities",
        "people_count",
        "detections",
        "features",
        "model_name",
    ):
        assert key in payload, f"missing key: {key}"

    assert payload["density_label"] in {"LOW", "MEDIUM", "HIGH"}
    assert 0.0 <= float(payload["confidence"]) <= 1.0
    assert isinstance(payload["detections"], list)
    assert payload["model_name"]


def test_analyze_frame_rejects_invalid_image(client):
    response = client.post(
        "/analyze/frame",
        files={"file": ("bad.jpg", b"not-an-image", "image/jpeg")},
    )
    assert response.status_code == 400


def test_analyze_frame_serializes_detections(client, monkeypatch):
    """Regression: /analyze/frame returned 500 whenever people were detected.

    The serialization loop read ``d.class_id``, but the Detection dataclass
    only has (bbox, confidence, person_id). The plain-image contract test
    never hit it because an all-black frame detects zero people.
    """
    from api.routers import detector as real_detector
    from computer_vision.person_detection import Detection

    fake_detections = [
        Detection(bbox=(10, 20, 60, 180), confidence=0.91, person_id=7),
        Detection(bbox=(70, 30, 130, 190), confidence=0.77, person_id=None),
    ]
    monkeypatch.setattr(real_detector, "detect", lambda frame: fake_detections)

    response = client.post(
        "/analyze/frame",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200

    dets = response.json()["detections"]
    assert len(dets) == 2

    first, second = dets
    assert first["bbox"] == [10.0, 20.0, 60.0, 180.0]
    assert first["class_id"] == 0
    assert first["person_id"] == 7
    assert second["person_id"] is None
    assert 0.0 <= first["confidence"] <= 1.0


# ── Dataset endpoints ────────────────────────────────────────────────────────

def test_dataset_info(client):
    response = client.get("/dataset/info")
    assert response.status_code == 200

    payload = response.json()
    assert payload["exists"] is True
    assert payload["n_rows"] > 0
    assert len(payload["feature_columns"]) == 10
    assert payload["class_labels"] == ["LOW", "MEDIUM", "HIGH"]
    assert set(payload["class_counts"]).issubset({"LOW", "MEDIUM", "HIGH"})


def test_dataset_preview(client):
    response = client.get("/dataset/preview", params={"limit": 50})
    assert response.status_code == 200

    payload = response.json()
    assert payload["n_preview_rows"] == 50
    assert payload["n_rows"] >= payload["n_preview_rows"]
    assert "density_label" in payload["columns"]
    assert len(payload["rows"]) == payload["n_preview_rows"]
    assert len(payload["rows"][0]) == len(payload["columns"])


def test_dataset_generate_validates_bounds(client):
    response = client.post("/dataset/generate", params={"n_per_class": 10})
    assert response.status_code == 400
    assert "error" in response.json()


# ── Model registry endpoints ─────────────────────────────────────────────────

def test_models_list(client):
    response = client.get("/models/list")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload["artifacts"]) == 7
    assert payload["has_trained_models"] is True
    assert payload["class_labels"] == ["LOW", "MEDIUM", "HIGH"]

    for name, artifact in payload["artifacts"].items():
        assert artifact["file"].endswith(".joblib"), name
        assert isinstance(artifact["present"], bool)


def test_models_evaluation_shape(client):
    response = client.get("/models/evaluation")
    assert response.status_code == 200

    payload = response.json()
    assert payload["val_metrics"], "expected validation metrics"
    assert payload["best_model_name"] in payload["val_metrics"]

    for metrics in payload["val_metrics"].values():
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["f1_weighted"] <= 1.0
        assert "classification_report" in metrics

        cm = metrics["confusion_matrix"]
        assert len(cm) == 3
        assert all(len(row) == 3 for row in cm)


def test_feature_importance(client):
    response = client.get("/models/feature-importance")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload["feature_names"]) == len(payload["importances"]) == 10
    assert all(isinstance(v, float) for v in payload["importances"])


def test_models_train_writes_to_isolated_dir(client, monkeypatch, tmp_path):
    """Training must run end-to-end without mutating the repository artifacts."""
    import machine_learning.preprocessing as preprocessing
    import machine_learning.train as train_module

    isolated = str(tmp_path / "models")
    monkeypatch.setattr(preprocessing, "MODELS_DIR", isolated, raising=False)
    monkeypatch.setattr(train_module, "MODELS_DIR", isolated, raising=False)

    response = client.post("/models/train")
    assert response.status_code == 200

    payload = response.json()
    assert payload["trained"] is True
    assert len(payload["val_metrics"]) == 7
    assert payload["best_model_name"] in payload["val_metrics"]

    import os

    assert os.path.exists(os.path.join(isolated, "best_model.joblib"))
    assert os.path.exists(os.path.join(isolated, "evaluation_results.joblib"))
