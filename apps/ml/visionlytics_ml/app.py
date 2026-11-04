"""
Visionlytics ML service (Phase 3):
- Real ONNX Runtime object detection (`RT-DETRv2-R18vd-INT8` & `YOLOS-Tiny-INT8`)
- Multi-object tracking (`ByteTrackerWithReID`) with Kalman smoothing, EMA class voting,
  and re-ID occlusion recovery
- Foreground-masked CIELAB + CIEDE2000 colour extraction & person upper/lower clothing split
- Live evaluation harness metrics endpoint (`/eval/metrics`)
"""
from __future__ import annotations

import base64
import io
import json
import platform

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel, Field

from .detector import VisionDetector
from .eval_harness import LATEST_PATH, GOLDEN_DIR, run_full_evaluation
from .tracker import ByteTrackerWithReID

app = FastAPI(title="Visionlytics ML", version="0.3.0")
detector = VisionDetector()
stream_trackers: dict[str, ByteTrackerWithReID] = {}


class Base64AnalyzeRequest(BaseModel):
    imageBase64: str
    preset: str = Field(default="balanced", pattern="^(fast|balanced|max_accuracy)$")
    minConfidence: float = Field(default=0.28, ge=0.05, le=0.99)
    uncertainThreshold: float = Field(default=0.50, ge=0.10, le=0.99)
    tiled: bool = False
    openVocabQuery: str | None = None
    streamId: str | None = None
    frameIndex: int = 0


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/runtime")
def runtime() -> dict[str, object]:
    return {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "onnxruntime": ort.__version__,
        "providers": ort.get_available_providers(),
    }


@app.get("/eval/metrics")
def get_eval_metrics(refresh: bool = False) -> dict[str, object]:
    if refresh or not LATEST_PATH.exists():
        return run_full_evaluation()
    with open(LATEST_PATH) as f:
        return json.load(f)  # type: ignore[no-any-return]


@app.get("/samples")
def list_samples() -> dict[str, object]:
    """Returns built-in golden evaluation images as base64 data URLs for one-click testing."""
    items: list[dict[str, str]] = []
    for name, title in [
        ("bus_street.jpg", "Urban transit & pedestrians (810×1080)"),
        ("zidane_people.jpg", "Close-range subjects & attire (1280×720)"),
    ]:
        p = GOLDEN_DIR / name
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            items.append(
                {
                    "id": name,
                    "title": title,
                    "dataUrl": f"data:image/jpeg;base64,{b64}",
                }
            )
    return {"items": items}


@app.post("/infer/base64")
def infer_base64(req: Base64AnalyzeRequest) -> dict[str, object]:
    raw_b64 = req.imageBase64
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]
    try:
        img_bytes = base64.b64decode(raw_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image payload: {exc}") from exc

    result = detector.analyze_image(
        img,
        preset=req.preset,
        min_confidence=req.minConfidence,
        uncertain_threshold=req.uncertainThreshold,
        tiled=req.tiled,
        open_vocab_query=req.openVocabQuery,
    )

    if req.streamId:
        tracker = stream_trackers.get(req.streamId)
        if tracker is None:
            tracker = ByteTrackerWithReID(
                enter_threshold=req.uncertainThreshold,
                exit_threshold=req.minConfidence,
            )
            stream_trackers[req.streamId] = tracker
        frame_np = np.asarray(img)
        tracked = tracker.step(
            list(result["detections"]),  # type: ignore[arg-type]
            frame_np,
            frame_index=req.frameIndex,
        )
        result["detections"] = tracked
        result["uniqueTrackCount"] = len(tracker.tracks)

    return result


@app.post("/infer/upload")
async def infer_upload(
    file: UploadFile = File(...),
    preset: str = Form("balanced"),
    minConfidence: float = Form(0.28),
    uncertainThreshold: float = Form(0.50),
    tiled: bool = Form(False),
    openVocabQuery: str | None = Form(None),
) -> dict[str, object]:
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid uploaded image: {exc}") from exc

    return detector.analyze_image(
        img,
        preset=preset,
        min_confidence=minConfidence,
        uncertain_threshold=uncertainThreshold,
        tiled=tiled,
        open_vocab_query=openVocabQuery,
    )
