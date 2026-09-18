import requests
import cv2
import numpy as np

import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

def analyze_frame_api(frame: np.ndarray):
    """Send a frame to the FastAPI backend for analysis."""
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()
    
    try:
        response = requests.post(
            f"{API_URL}/analyze/frame",
            files={"file": ("frame.jpg", img_bytes, "image/jpeg")},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    
    return None
