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
        "attributes",
        "tracking",
        "features",
        "model_name",
    ):
        assert key in payload, f"missing key: {key}"

    assert payload["density_label"] in {"LOW", "MEDIUM", "HIGH"}
    assert 0.0 <= float(payload["confidence"]) <= 1.0
    assert isinstance(payload["detections"], list)
    assert isinstance(payload["attributes"], list)
    assert payload["tracking"] is False
    assert payload["model_name"]


def test_analyze_frame_rejects_invalid_image(client):
    response = client.post(
        "/analyze/frame",
        files={"file": ("bad.jpg", b"not-an-image", "image/jpeg")},
    )
    assert response.status_code == 400


def test_analyze_frame_applies_confidence_override(client, monkeypatch):
    """The request's `confidence` must reach the detector without mutating it."""
    from api.routers import detector as real_detector

    seen = {}

    def fake_detect(image, confidence=None):
        seen["confidence"] = confidence
        seen["instance_default"] = real_detector.confidence_threshold
        return []

    monkeypatch.setattr(real_detector, "detect", fake_detect)

    response = client.post(
        "/analyze/frame",
        params={"confidence": 0.75},
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200
    assert seen["confidence"] == 0.75
    # Instance default is left untouched, so concurrent requests can't interfere.
    assert seen["instance_default"] != 0.75
    assert real_detector.confidence_threshold == seen["instance_default"]


def test_analyze_frame_confidence_is_validated(client):
    response = client.post(
        "/analyze/frame",
        params={"confidence": 5.0},
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_analyze_frame_tracking_populates_person_ids(client, monkeypatch):
    """`track=true` must use ByteTrack and return person_id per detection."""
    from api.routers import detector as real_detector
    from computer_vision.person_detection import Detection

    calls = {"track": 0, "detect": 0}

    def fake_track(image, persist=True, confidence=None):
        calls["track"] += 1
        return [Detection(bbox=(5, 5, 40, 90), confidence=0.8, person_id=3)]

    def fake_detect(image, confidence=None):
        calls["detect"] += 1
        return []

    monkeypatch.setattr(real_detector, "track", fake_track)
    monkeypatch.setattr(real_detector, "detect", fake_detect)

    response = client.post(
        "/analyze/frame",
        params={"track": True},
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["tracking"] is True
    assert payload["detections"][0]["person_id"] == 3
    assert calls == {"track": 1, "detect": 0}


def test_analyze_frame_attributes_are_optional(client, monkeypatch):
    """Attribute estimation is opt-in and returns one entry per detection."""
    from api.routers import detector as real_detector
    from computer_vision.person_detection import Detection

    monkeypatch.setattr(
        real_detector,
        "detect",
        lambda image, confidence=None: [
            Detection(bbox=(10, 20, 80, 190), confidence=0.9),
        ],
    )

    without = client.post(
        "/analyze/frame",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert without.status_code == 200
    assert without.json()["attributes"] == []

    with_attrs = client.post(
        "/analyze/frame",
        params={"attributes": True},
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert with_attrs.status_code == 200

    attributes = with_attrs.json()["attributes"]
    assert len(attributes) == 1
    assert set(attributes[0]) == {
        "hair_color",
        "clothing_color",
        "hair_confidence",
        "clothing_confidence",
        "apparent_sex",
    }
    assert attributes[0]["apparent_sex"] == "UNKNOWN"


def test_csrnet_count_is_downscaled_and_rescaled(monkeypatch):
    """CSRNet must not run at native resolution, but counts must match it.

    Running the network on multi-megapixel frames took seconds per frame and
    dominated video analysis latency.
    """
    from api import routers

    seen = {}

    def fake_estimate(tensor, model):
        seen["shape"] = tuple(tensor.shape[-2:])
        # Density sums scale with pixel area in the shipped checkpoint.
        return tensor.shape[-2] * tensor.shape[-1]

    monkeypatch.setattr(routers, "estimate_dense_crowd", fake_estimate)

    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    count = routers._csrnet_count(frame)

    assert max(seen["shape"]) == routers.CSRNET_MAX_SIDE
    native_pixels = 720 * 1280
    assert abs(count - native_pixels) / native_pixels < 0.02


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
    monkeypatch.setattr(real_detector, "detect", lambda image, confidence=None: fake_detections)

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


@pytest.mark.slow
def test_models_train_writes_to_isolated_dir(client, monkeypatch, tmp_path):
    """Training must run end-to-end without mutating the repository artifacts.

    Trains all 7 models (~2 minutes on a busy machine), so it is tagged `slow`:
    deselect with `pytest -m "not slow"` for fast local iterations.
    """
    import machine_learning.preprocessing as preprocessing
    import machine_learning.train as train_module

    isolated = str(tmp_path / "models")
    monkeypatch.setattr(preprocessing, "MODELS_DIR", isolated, raising=False)
    monkeypatch.setattr(train_module, "MODELS_DIR", isolated, raising=False)

    response = client.post("/models/train")
    assert response.status_code == 200

    payload = response.json()
    # 8 models trained: Logistic Regression, KNN, Decision Tree, Random Forest,
    # SVM, Gradient Boosting, XGBoost, and Voting Ensemble.
    assert len(payload["val_metrics"]) == 8
    assert payload["best_model_name"] in payload["val_metrics"]

    import os

    assert os.path.exists(os.path.join(isolated, "best_model.joblib"))
    assert os.path.exists(os.path.join(isolated, "evaluation_results.joblib"))
