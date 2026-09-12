"""
Person Detection Module for Visionlytics.

Uses YOLOv8s to detect people in images and video frames. The detector filters
for the COCO person class and returns structured detections with optional
tracking IDs and lightweight visual attributes.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any


@dataclass
class Detection:
    """Represents one detected person."""

    bbox: Tuple[int, int, int, int]
    confidence: float
    person_id: Optional[int] = None
    class_id: int = 0
    class_name: str = "person"
    attributes: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.attributes is None:
            self.attributes = {}

    @property
    def center(self) -> Tuple[float, float]:
        """Return the center point of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def area(self) -> int:
        """Return the bounding-box area in pixels."""
        x1, y1, x2, y2 = self.bbox
        return max(0, x2 - x1) * max(0, y2 - y1)

    @property
    def width(self) -> int:
        """Return the bounding-box width."""
        return max(0, self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> int:
        """Return the bounding-box height."""
        return max(0, self.bbox[3] - self.bbox[1])


class PersonDetector:
    """Detect and track people using YOLOv8s."""

    PERSON_CLASS_ID = 0

    def __init__(self, confidence_threshold: float = 0.3, max_image_size: int = 640):
        self.confidence_threshold = confidence_threshold
        self.max_image_size = max_image_size
        self._model = None

    def _load_model(self):
        """Lazily load the YOLOv8s model, preferring ONNX when available."""
        if self._model is None:
            from ultralytics import YOLO
            import os

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            onnx_path = os.path.join(project_root, "yolov8s.onnx")
            pt_path = os.path.join(project_root, "yolov8s.pt")

            if os.path.exists(onnx_path):
                self._model = YOLO(onnx_path, task="detect")
            elif os.path.exists(pt_path):
                self._model = YOLO(pt_path)
            else:
                raise FileNotFoundError(
                    "No YOLOv8s model found. Expected 'yolov8s.onnx' or 'yolov8s.pt' in the project root."
                )

        return self._model

    @staticmethod
    def _device() -> str:
        """Select a safe inference device for the current platform."""
        import sys

        if sys.platform == "darwin":
            return "cpu"

        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def detect(self, image: np.ndarray) -> List[Detection]:
        """Detect people in a BGR image."""
        if image is None or image.size == 0:
            return []

        model = self._load_model()
        results = model.predict(
            source=image,
            conf=self.confidence_threshold,
            classes=[self.PERSON_CLASS_ID],
            imgsz=self.max_image_size,
            device=self._device(),
            verbose=False,
        )

        detections: List[Detection] = []
        if not results:
            return detections

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes = result.boxes
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
            confidence = float(boxes.conf[i].cpu().numpy())
            detections.append(
                Detection(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    confidence=confidence,
                )
            )

        return detections

    def track(self, image: np.ndarray, persist: bool = True) -> List[Detection]:
        """Detect and track people in a BGR image using ByteTrack."""
        if image is None or image.size == 0:
            return []

        model = self._load_model()
        results = model.track(
            source=image,
            conf=self.confidence_threshold,
            classes=[self.PERSON_CLASS_ID],
            imgsz=self.max_image_size,
            device=self._device(),
            tracker="bytetrack.yaml",
            persist=persist,
            verbose=False,
        )

        detections: List[Detection] = []
        if not results:
            return detections

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes = result.boxes
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
            confidence = float(boxes.conf[i].cpu().numpy())
            person_id = None
            if boxes.id is not None:
                person_id = int(boxes.id[i].cpu().numpy())

            detections.append(
                Detection(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    confidence=confidence,
                    person_id=person_id,
                )
            )

        return detections

    def detect_and_draw(
        self,
        image: np.ndarray,
        density_level: str = "LOW",
        show_labels: bool = True,
        max_labels: int = 20,
    ) -> Tuple[np.ndarray, List[Detection]]:
        """Detect people and draw bounding boxes."""
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
        """Draw bounding boxes for the supplied detections."""
        annotated = image.copy()

        color_map = {
            "LOW": (0, 200, 0),
            "MEDIUM": (0, 180, 255),
            "HIGH": (0, 0, 255),
        }
        color = color_map.get(density_level, (0, 200, 0))

        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            if show_labels and i < max_labels:
                label_id = det.person_id if det.person_id is not None else (i + 1)
                label = f"Person #{label_id}"
                (text_w, text_h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                label_top = max(0, y1 - text_h - 8)
                cv2.rectangle(
                    annotated,
                    (x1, label_top),
                    (x1 + text_w + 4, y1),
                    color,
                    -1,
                )
                cv2.putText(
                    annotated,
                    label,
                    (x1 + 2, max(text_h + 2, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        cv2.putText(
            annotated,
            f"People: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            color,
            2,
            cv2.LINE_AA,
        )

        return annotated
