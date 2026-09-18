"""
Person Detection Module for Visionlytics.

Uses YOLOv8n (nano) — a lightweight pretrained object detection model — to detect
people in images and video frames. The detector filters for class 'person' only
and returns bounding boxes with confidence scores.

This module handles the computer vision detection step. The extracted bounding boxes
are then passed to the feature extraction module for statistical analysis.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


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
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    person_id: Optional[int] = None

    @property
    def center(self) -> Tuple[float, float]:
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


class PersonDetector:
    """
    Detects people in images using YOLOv8s.

    The detector loads the YOLOv8s model on first use and caches it.
    Only detections of class 'person' (COCO class 0) are returned.

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

    def _load_model(self):
        """Lazily load the YOLOv8s model on first use, preferring ONNX for speed."""
        if self._model is None:
            from ultralytics import YOLO
            import os
            
            PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            onnx_path = os.path.join(PROJECT_ROOT, "yolov8s.onnx")
            pt_path = os.path.join(PROJECT_ROOT, "yolov8s.pt")
            
            if os.path.exists(onnx_path):
                # Using ONNX format
                self._model = YOLO(onnx_path, task='detect')
            else:
                # YOLOv8s is the small variant — offers much higher accuracy than nano while remaining fast
                self._model = YOLO(pt_path)
        return self._model

    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        Detect people in an image.

        Args:
            image: Input image as a NumPy array (BGR format from OpenCV).

        Returns:
            List of Detection objects for each person found.
        """
        if image is None or image.size == 0:
            return []

        model = self._load_model()

        import sys
        if sys.platform == "darwin":
            device = "cpu"  # Force CPU to prevent MPS threading segfaults on Mac
        else:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Resize if the image is too large (preserves aspect ratio internally)
        results = model.predict(
            source=image,
            conf=self.confidence_threshold,
            classes=[self.PERSON_CLASS_ID],  # Only detect people
            imgsz=self.max_image_size,
            device=device,
            verbose=False,
        )

        detections = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                for i in range(len(boxes)):
                    # Get bounding box coordinates in original image space
                    x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
                    conf = float(boxes.conf[i].cpu().numpy())

                    detections.append(Detection(
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        confidence=conf,
                    ))

        return detections

    def track(self, image: np.ndarray, persist: bool = True) -> List[Detection]:
        """
        Detect and track people in an image using ByteTrack.
        
        Args:
            image: Input image.
            persist: Whether to persist tracks across frames.

        Returns:
            List of Detection objects with person_id populated.
        """
        if image is None or image.size == 0:
            return []

        model = self._load_model()

        import sys
        if sys.platform == "darwin":
            device = "cpu"
        else:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"

        results = model.track(
            source=image,
            conf=self.confidence_threshold,
            classes=[self.PERSON_CLASS_ID],
            imgsz=self.max_image_size,
            device=device,
            tracker="bytetrack.yaml",
            persist=persist,
            verbose=False,
        )

        detections = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                for i in range(len(boxes)):
                    x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
                    conf = float(boxes.conf[i].cpu().numpy())
                    
                    person_id = None
                    if boxes.id is not None:
                        person_id = int(boxes.id[i].cpu().numpy())

                    detections.append(Detection(
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        confidence=conf,
                        person_id=person_id,
                    ))

        return detections

    def detect_and_draw(
        self,
        image: np.ndarray,
        density_level: str = "LOW",
        show_labels: bool = True,
        max_labels: int = 20,
    ) -> Tuple[np.ndarray, List[Detection]]:
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
        detections: List[Detection],
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
                conf_text = f"{det.confidence:.0%}"

                # Background rectangle for text
                (text_w, text_h), baseline = cv2.getTextSize(
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
