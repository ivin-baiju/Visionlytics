"""Visionlytics ML service. Phase 1 exposes health and runtime introspection only;
inference endpoints are added in Phase 3 once models are selected by benchmark."""
import platform

import onnxruntime as ort
from fastapi import FastAPI

app = FastAPI(title="Visionlytics ML", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/runtime")
def runtime() -> dict[str, object]:
    """Reports the real execution providers available on this host, so the UI and
    benchmarks can state honestly whether numbers came from CPU, CoreML or CUDA."""
    return {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "onnxruntime": ort.__version__,
        "providers": ort.get_available_providers(),
    }
