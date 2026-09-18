import io
import time
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from PIL import Image

from computer_vision.person_detection import PersonDetector
from computer_vision.feature_extraction import FeatureExtractor
from computer_vision.csrnet import CSRNet, estimate_dense_crowd
from machine_learning.predict import CrowdPredictor
from db.firebase_client import db_client
import torch
import torchvision.transforms as transforms

router = APIRouter()

detector = PersonDetector(confidence_threshold=0.3)
extractor = FeatureExtractor()
predictor = CrowdPredictor()

# Load CSRNet
csrnet_model = CSRNet(load_weights=False)
csrnet_model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@router.post("/analyze/frame")
async def analyze_frame(file: UploadFile = File(...)):
    """Analyze a single frame and return density, features, and tracking info."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return JSONResponse(status_code=400, content={"error": "Invalid image"})

    h, w = frame.shape[:2]
    
    # 1. Base YOLO Detection
    detections = detector.detect(frame)
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
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        img_tensor = transform(pil_img).unsqueeze(0)
        csr_count = estimate_dense_crowd(img_tensor, csrnet_model)
        
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
            "class_id": int(d.class_id),
            "person_id": int(d.person_id) if d.person_id else None
        })

    return {
        "density_label": density_label,
        "confidence": conf,
        "probabilities": probs,
        "people_count": people_count,
        "detections": det_list,
        "features": features
    }
