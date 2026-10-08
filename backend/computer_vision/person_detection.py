"""
Person Detection Module for Visionlytics.

Uses YOLOv8s — a lightweight pretrained object detection model — to detect
people in images and video frames. The detector filters for class 'person' only
and returns bounding boxes with confidence scores.

Performance Strategy:
    - ONNX Runtime is the PRIMARY inference backend (2-4x faster than PyTorch on CPU)
    - PyTorch (.pt) is used as a fallback only when ONNX is unavailable
    - Model is loaded once at construction and reused across all requests
    - Device selection is cached (no per-frame platform checks)

This module handles the computer vision detection step. The extracted bounding boxes
are then passed to the feature extraction module for statistical analysis.
"""

import os
import sys
from dataclasses import dataclass
from functools import lru_cache

import cv2
import numpy as np


@dataclass
class Detection:
    """
    Represents a single person detection.

    Attributes:
        bbox: Bounding box as (x1, y1, x2, y2) in pixel coordinates.
        confidence: Detection confidence score between 0 and 1.
        person_id: Optional tracking ID assigned by the tracker.
        center: Center point (cx, cy) of the bounding box.
        area: Area of the bounding box in pixels.
    """
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    person_id: int | None = None

    @property
    def center(self) -> tuple[float, float]:
        """Calculate the center point of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def area(self) -> int:
        """Calculate the area of the bounding box in pixels."""
        x1, y1, x2, y2 = self.bbox
        return max(0, (x2 - x1)) * max(0, (y2 - y1))

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]


@lru_cache(maxsize=1)
def _resolve_device() -> str:
    """Resolve the best available device once and cache it."""
    if sys.platform == "darwin":
        return "cpu"  # Force CPU to prevent MPS threading segfaults on Mac
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


@lru_cache(maxsize=1)
def _resolve_model_paths() -> tuple[str | None, str]:
    """Find ONNX and PT model paths once and cache the result."""
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [PROJECT_ROOT, os.path.dirname(PROJECT_ROOT)]

    onnx_path = None
    pt_path = "yolov8s.pt"  # fallback to download

    for d in search_dirs:
        cand_onnx = os.path.join(d, "yolov8s.onnx")
        if os.path.exists(cand_onnx) and onnx_path is None:
            onnx_path = cand_onnx
        cand_pt = os.path.join(d, "yolov8s.pt")
        if os.path.exists(cand_pt):
            pt_path = cand_pt

    return onnx_path, pt_path


class PersonDetector:
    """
    Detects people in images using YOLOv8s.

    Performance Notes:
        - ONNX Runtime is preferred over PyTorch for 2-4x CPU speedup
        - Model is loaded eagerly on first use and cached for the process lifetime
        - Device detection is cached globally (no per-frame overhead)

    Parameters:
        confidence_threshold: Minimum confidence score to keep a detection.
                              Lower values detect more people but with more
                              false positives. Default is 0.3.
        max_image_size: Maximum dimension (width or height) for input images.
                        Larger images are resized to this size while preserving
                        aspect ratio, for performance. Default is 640.
    """

    # COCO class index for 'person'
    PERSON_CLASS_ID = 0

    def __init__(self, confidence_threshold: float = 0.3, max_image_size: int = 640):
        self.confidence_threshold = confidence_threshold
        self.max_image_size = max_image_size
        self._model = None
        self._device = _resolve_device()

    def _load_model(self):
        """Load the YOLOv8s model, preferring ONNX for speed."""
        if self._model is None:
            from ultralytics import YOLO

            onnx_path, pt_path = _resolve_model_paths()

            if onnx_path and os.path.exists(onnx_path):
                # ONNX Runtime: 2-4x faster than PyTorch on CPU
                self._model = YOLO(onnx_path, task='detect')
            else:
                self._model = YOLO(pt_path)
        return self._model

    def warm_up(self):
        """Pre-load model weights and run a dummy frame to eliminate first-request latency."""
        self._load_model()
        dummy = np.zeros((320, 320, 3), dtype=np.uint8)
        self.detect(dummy)

    @staticmethod
    def _parse_results(results) -> list[Detection]:
        """Extract Detection objects from YOLO results (shared by detect/track)."""
        detections = []
        if not results or len(results) == 0:
            return detections

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes = result.boxes
        # Batch extract all boxes at once (single CPU transfer)
        xyxy = boxes.xyxy.cpu().numpy().astype(int)
        confs = boxes.conf.cpu().numpy()
        ids = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else None

        for i in range(len(boxes)):
            x1, y1, x2, y2 = xyxy[i]
            detections.append(Detection(
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                confidence=float(confs[i]),
                person_id=int(ids[i]) if ids is not None else None,
            ))

        return detections

    def detect(self, image: np.ndarray, confidence: float | None = None) -> list[Detection]:
        """
        Detect people in an image.

        Args:
            image: Input image as a NumPy array (BGR format from OpenCV).
            confidence: Optional per-call confidence threshold override. Keeps
                        the instance default free of cross-request races when
                        the API serves concurrent requests.

        Returns:
            List of Detection objects for each person found.
        """
        if image is None or image.size == 0:
            return []

        model = self._load_model()
        conf_threshold = self.confidence_threshold if confidence is None else float(confidence)

        results = model.predict(
            source=image,
            conf=conf_threshold,
            classes=[self.PERSON_CLASS_ID],
            imgsz=self.max_image_size,
            device=self._device,
            verbose=False,
        )

        return self._parse_results(results)

    def track(
        self,
        image: np.ndarray,
        persist: bool = True,
        confidence: float | None = None,
    ) -> list[Detection]:
        """
        Detect and track people in an image using ByteTrack.

        Args:
            image: Input image.
            persist: Whether to persist tracks across frames.
            confidence: Optional per-call confidence threshold override.

        Returns:
            List of Detection objects with person_id populated.
        """
        if image is None or image.size == 0:
            return []

        model = self._load_model()
        conf_threshold = self.confidence_threshold if confidence is None else float(confidence)

        results = model.track(
            source=image,
            conf=conf_threshold,
            classes=[self.PERSON_CLASS_ID],
            imgsz=self.max_image_size,
            device=self._device,
            tracker="bytetrack.yaml",
            persist=persist,
            verbose=False,
        )

        return self._parse_results(results)

    def detect_and_draw(
        self,
        image: np.ndarray,
        density_level: str = "LOW",
        show_labels: bool = True,
        max_labels: int = 20,
    ) -> tuple[np.ndarray, list[Detection]]:
        """
        Detect people and draw bounding boxes on the image.

        Args:
            image: Input image (BGR).
            density_level: Current crowd density for color coding.
            show_labels: Whether to show person labels.
            max_labels: Maximum number of labels to display (avoids clutter).

        Returns:
            Tuple of (annotated_image, detections).
        """
        detections = self.detect(image)
        annotated = self.draw_detections(
            image, detections, density_level, show_labels, max_labels
        )
        return annotated, detections

    @staticmethod
    def draw_detections(
        image: np.ndarray,
        detections: list[Detection],
        density_level: str = "LOW",
        show_labels: bool = True,
        max_labels: int = 20,
    ) -> np.ndarray:
        """
        Draw bounding boxes on an image for the given detections.

        Color coding by density level:
            LOW    → Green  (0, 200, 0)
            MEDIUM → Amber  (0, 180, 255)
            HIGH   → Red    (0, 0, 255)

        Args:
            image: Input image (BGR).
            detections: List of Detection objects.
            density_level: Density level for color selection.
            show_labels: Whether to show person number labels.
            max_labels: Maximum number of labels to show.

        Returns:
            Annotated image copy.
        """
        annotated = image.copy()

        # Color map by density level
        color_map = {
            "LOW": (0, 200, 0),       # Green
            "MEDIUM": (0, 180, 255),   # Amber
            "HIGH": (0, 0, 255),       # Red
        }
        color = color_map.get(density_level, (0, 200, 0))

        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det.bbox

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label (limit to avoid visual clutter)
            if show_labels and i < max_labels:
                label_id = det.person_id if det.person_id is not None else (i + 1)
                label = f"Person #{label_id}"

                # Background rectangle for text
                (text_w, text_h), _baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                cv2.rectangle(
                    annotated,
                    (x1, y1 - text_h - 8),
                    (x1 + text_w + 4, y1),
                    color,
                    -1,
                )
                cv2.putText(
                    annotated,
                    label,
                    (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        # Draw count overlay in top-left corner
        count_text = f"People: {len(detections)}"
        cv2.putText(
            annotated,
            count_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            color,
            2,
            cv2.LINE_AA,
        )

        return annotated
