import cv2
import numpy as np
import torch
from computer_vision.attributes import estimate_all_attributes
from computer_vision.csrnet import CSRNet, estimate_dense_crowd
from computer_vision.feature_extraction import FeatureExtractor
from computer_vision.person_detection import PersonDetector
from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import JSONResponse
from machine_learning.predict import CrowdPredictor
from PIL import Image
from torchvision import transforms

router = APIRouter()

detector = PersonDetector(confidence_threshold=0.3)
extractor = FeatureExtractor()
predictor = CrowdPredictor()

import os

# Load CSRNet
csrnet_weights_path = os.path.join(os.path.dirname(__file__), '..', 'computer_vision', 'csrnet_epoch_10.pth')
if os.path.exists(csrnet_weights_path):
    csrnet_model = CSRNet(load_weights=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    csrnet_model.load_state_dict(torch.load(csrnet_weights_path, map_location=device, weights_only=True))
else:
    csrnet_model = CSRNet(load_weights=False)
    
csrnet_model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# CSRNet is a VGG16-sized fully-convolutional network. Running it at native
# frame resolution costs 1–2 seconds per frame on CPU. Its raw density-map sum
# scales with pixel area (measured empirically), so we downscale for speed and
# rescale the count back to native resolution to keep the fallback calibrated.
CSRNET_MAX_SIDE = 512


def _csrnet_count(frame: np.ndarray) -> int:
    """Crowd count from CSRNet, computed on a downscaled copy of the frame.

    The result is rescaled by the pixel-area ratio so that the reported count
    matches what the network produces at native resolution.
    """
    native_pixels = frame.shape[0] * frame.shape[1]

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    pil_img.thumbnail((CSRNET_MAX_SIDE, CSRNET_MAX_SIDE))
    resized_pixels = pil_img.size[0] * pil_img.size[1]

    img_tensor = transform(pil_img).unsqueeze(0)
    raw_count = estimate_dense_crowd(img_tensor, csrnet_model)

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
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return JSONResponse(status_code=400, content={"error": "Invalid image"})

    h, w = frame.shape[:2]
    
    # 1. Base YOLO Detection (ByteTrack when tracking is requested)
    if track:
        detections = detector.track(frame, confidence=confidence)
    else:
        detections = detector.detect(frame, confidence=confidence)
    features = extractor.extract(detections, (h, w))
    
    # 2. Density Prediction
    if predictor.is_loaded:
        density_label, conf = predictor.predict(features)
        probs = predictor.predict_proba(features)
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

    # 4. Save to Firebase (or SQLite fallback)
    # db_client.save_analysis("api", features, density_label, conf)

    # Convert detections to serializable format
    det_list = []
    for d in detections:
        det_list.append({
            "bbox": [float(x) for x in d.bbox],
            "confidence": float(d.confidence),
            # Detection has no class_id field — the detector only ever
            # returns COCO person (class 0).
            "class_id": int(detector.PERSON_CLASS_ID),
            "person_id": int(d.person_id) if d.person_id else None
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
        "model_name": predictor.model_name if predictor.is_loaded else "Heuristic Fallback",
    }
