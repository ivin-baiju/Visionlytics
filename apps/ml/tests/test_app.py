import base64
from pathlib import Path

from fastapi.testclient import TestClient

from visionlytics_ml.app import app
from visionlytics_ml.eval_harness import check_regression_gate

client = TestClient(app)


def test_healthz() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_runtime_lists_cpu_provider() -> None:
    body = client.get("/runtime").json()
    assert "CPUExecutionProvider" in body["providers"]


def test_eval_metrics_and_regression_gate() -> None:
    res = client.get("/eval/metrics")
    assert res.status_code == 200
    report = res.json()
    assert report["metrics"]["mAP50"] >= 0.85
    assert report["metrics"]["colourNamingAccuracy"] >= 0.80
    passed, reasons = check_regression_gate(report)
    assert passed, f"Regression gate failed: {reasons}"


def test_infer_base64_and_open_vocab_filter() -> None:
    img_path = Path(__file__).resolve().parent.parent / "data" / "golden" / "bus_street.jpg"
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    res = client.post(
        "/infer/base64",
        json={
            "imageBase64": b64,
            "preset": "balanced",
            "minConfidence": 0.30,
            "uncertainThreshold": 0.50,
            "streamId": "test-stream-1",
            "frameIndex": 0,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["peopleCount"] == 4
    labels = [d["label"] for d in body["detections"]]
    assert "bus" in labels
    assert "person" in labels
    person_det = next(d for d in body["detections"] if d["label"] == "person")
    assert len(person_det["colours"]) >= 1
    assert "upperClothingColours" in person_det
    assert "lowerClothingColours" in person_det
