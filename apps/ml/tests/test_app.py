from fastapi.testclient import TestClient

from visionlytics_ml.app import app

client = TestClient(app)


def test_healthz() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_runtime_lists_cpu_provider() -> None:
    body = client.get("/runtime").json()
    assert "CPUExecutionProvider" in body["providers"]
