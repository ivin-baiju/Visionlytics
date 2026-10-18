import base64
import os

import cv2
import numpy as np
import torch
from computer_vision.attributes import estimate_all_attributes
from computer_vision.csrnet import CSRNet, estimate_dense_crowd
from computer_vision.feature_extraction import FeatureExtractor
from computer_vision.person_detection import PersonDetector
from db.supabase_client import supabase_client
from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import JSONResponse
from machine_learning.predict import CrowdPredictor
from PIL import Image
from torchvision import transforms

router = APIRouter()

# 12 MB upload cap — prevents OOM / DoS from giant images.
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
# Downscale inputs larger than this before YOLO (speed + memory).
MAX_FRAME_SIDE = 1920

_detector: PersonDetector | None = None
_extractor: FeatureExtractor | None = None
_predictor: CrowdPredictor | None = None
_csrnet_model = None
_csrnet_device = None


# Module-level singletons. PersonDetector()/FeatureExtractor()/CrowdPredictor()
# construction is cheap (no weights loaded until first use), so importing this
# module stays fast and tests can monkeypatch `detector.detect` directly.
detector = PersonDetector(confidence_threshold=0.3)
extractor = FeatureExtractor()
predictor = CrowdPredictor()


def get_detector() -> PersonDetector:
    return detector


def get_extractor() -> FeatureExtractor:
    return extractor


def get_predictor() -> CrowdPredictor:
    return predictor


def get_csrnet():
    """Lazily load CSRNet once; safe for import-time and offline envs."""
    global _csrnet_model, _csrnet_device
    if _csrnet_model is not None:
        return _csrnet_model, _csrnet_device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _csrnet_device = device
    weights_path = os.path.join(
        os.path.dirname(__file__), "..", "computer_vision", "csrnet_epoch_10.pth"
    )
    try:
        if os.path.exists(weights_path):
            _csrnet_model = CSRNet(load_weights=True)
            try:
                state = torch.load(weights_path, map_location=device, weights_only=True)
            except TypeError:
                # torch<2.4 has no weights_only kwarg
                state = torch.load(weights_path, map_location=device)
            _csrnet_model.load_state_dict(state)
        else:
            _csrnet_model = CSRNet(load_weights=False)
    except Exception as exc:
        print(f"[Visionlytics API] CSRNet load failed, using untrained init: {exc}")
        _csrnet_model = CSRNet(load_weights=False)
    _csrnet_model.to(device)
    _csrnet_model.eval()
    return _csrnet_model, device


# Backwards-compat alias for older imports/tests.
csrnet_model = None

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# CSRNet is a VGG16-sized fully-convolutional network. Running it at native
# frame resolution costs 1–2 seconds per frame on CPU. The shipped checkpoint's
# raw density-map sum scales with pixel area (pinned by
# test_csrnet_count_is_downscaled_and_rescaled), so we downscale for speed and
# rescale the count back to native resolution to keep the fallback calibrated.
CSRNET_MAX_SIDE = 512


def _csrnet_count(frame: np.ndarray) -> int:
    """Crowd count from CSRNet, computed on a downscaled copy of the frame.

    The result is rescaled by the pixel-area ratio so that the reported count
    matches what the network produces at native resolution.
    """
    native_pixels = frame.shape[0] * frame.shape[1]
    model, device = get_csrnet()
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb).copy()
    pil_img.thumbnail((CSRNET_MAX_SIDE, CSRNET_MAX_SIDE))
    resized_pixels = pil_img.size[0] * pil_img.size[1]
    img_tensor = transform(pil_img).unsqueeze(0).to(device)
    raw_count = estimate_dense_crowd(img_tensor, model)
    if resized_pixels <= 0:
        return raw_count
    return round(raw_count * native_pixels / resized_pixels)


@router.post("/analyze/frame")
async def analyze_frame(
    file: UploadFile = File(...),
    confidence: float | None = Query(
        default=None,
        ge=0.05,
        le=0.95,
        description="Per-request YOLO confidence threshold override.",
    ),
    track: bool = Query(
        default=False,
        description="Run ByteTrack tracking and populate person_id per detection.",
    ),
    attributes: bool = Query(
        default=False,
        description="Estimate hair/clothing colours for each detected person.",
    ),
):
    """Analyze a single frame and return density, features, and tracking info."""
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        return JSONResponse(status_code=413, content={"error": "Image too large (max 12 MB)"})
    if file.content_type and not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "File must be an image"})
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return JSONResponse(status_code=400, content={"error": "Invalid image"})

    # Downscale giant frames before inference (speed + memory guard).
    h0, w0 = frame.shape[:2]
    longest = max(h0, w0)
    if longest > MAX_FRAME_SIDE:
        scale = MAX_FRAME_SIDE / float(longest)
        frame = cv2.resize(frame, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_AREA)

    h, w = frame.shape[:2]
    det = get_detector()
    ext = get_extractor()
    pred = get_predictor()

    # 1. Base YOLO Detection (ByteTrack when tracking is requested)
    if track:
        detections = det.track(frame, confidence=confidence)
    else:
        detections = det.detect(frame, confidence=confidence)
    features = ext.extract(detections, (h, w))

    # 2. Density Prediction
    if pred.is_loaded:
        density_label, conf = pred.predict(features)
        probs = pred.predict_proba(features)
    else:
        # Fallback if models aren't trained
        density_label = "LOW"
        conf = 0.5
        probs = {"LOW": 0.5, "MEDIUM": 0.3, "HIGH": 0.2}

    # 3. High-Density CSRNet Fallback
    people_count = features["people_count"]
    if density_label == "HIGH" or people_count > 40:
        # Route to CSRNet for extreme dense counting
        csr_count = _csrnet_count(frame)
        
        # Override count if CSRNet detects more
        if csr_count > people_count:
            people_count = csr_count
            features["people_count"] = people_count

    # 4. Save to Database (Supabase with SQLite fallback) & Store upload record
    try:
        supabase_client.save_analysis("api", features, density_label, float(conf))
        
        # Generate lightweight preview thumbnail (max 200px width/height)
        thumb_h, thumb_w = frame.shape[:2]
        thumb_max = 200
        thumb_scale = min(thumb_max / float(max(thumb_h, thumb_w)), 1.0)
        thumb_img = cv2.resize(frame, (int(thumb_w * thumb_scale), int(thumb_h * thumb_scale)), interpolation=cv2.INTER_AREA)
        _, thumb_buf = cv2.imencode(".jpg", thumb_img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        thumb_b64 = "data:image/jpeg;base64," + base64.b64encode(thumb_buf).decode("utf-8")
        
        supabase_client.save_upload(
            filename=file.filename or "upload.jpg",
            file_size_bytes=len(contents),
            content_type=file.content_type or "image/jpeg",
            thumbnail_base64=thumb_b64,
            people_count=int(people_count),
            density_label=str(density_label),
            confidence=float(conf),
        )
    except Exception as exc:
        pass  # Non-blocking for inference response

    # Convert detections to serializable format
    det_list = []
    for d in detections:
        det_list.append({
            "bbox": [float(x) for x in d.bbox],
            "confidence": float(d.confidence),
            # Detection has no class_id field — the detector only ever
            # returns COCO person (class 0).
            "class_id": int(det.PERSON_CLASS_ID),
            "person_id": int(d.person_id) if d.person_id is not None else None
        })

    # 4. Optional visual attribute estimation (hair / clothing colours)
    attribute_list = []
    if attributes and detections:
        attribute_list = [
            {
                "hair_color": attr.hair_color,
                "clothing_color": attr.clothing_color,
                "hair_confidence": attr.hair_confidence,
                "clothing_confidence": attr.clothing_confidence,
                "apparent_sex": "UNKNOWN",
            }
            for attr in estimate_all_attributes(frame, detections)
        ]

    return {
        "density_label": density_label,
        "confidence": conf,
        "probabilities": probs,
        "people_count": people_count,
        "detections": det_list,
        "attributes": attribute_list,
        "tracking": bool(track),
        "features": features,
        "model_name": pred.model_name if pred.is_loaded else "Heuristic Fallback",
    }
