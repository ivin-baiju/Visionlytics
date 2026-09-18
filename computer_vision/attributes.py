"""
Visual Attribute Estimation Module for Visionlytics.

Provides best-effort estimation of visual attributes for detected people:
- Hair color estimation (from upper portion of person crop)
- Clothing color estimation (from lower portion of person crop)

IMPORTANT DISCLAIMER:
All attribute estimations are APPROXIMATE computer vision estimates based
on color histogram analysis. They can be inaccurate due to lighting,
occlusion, angle, image quality, and other factors.

These attributes are presented as secondary analytics and do NOT affect
the primary crowd density classification.
"""

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from computer_vision.person_detection import Detection

# ── Color Category Definitions ────────────────────────────────────────────────

# Hair color categories with their HSV ranges
# Format: (H_low, S_low, V_low, H_high, S_high, V_high)
HAIR_COLORS = {
    "BLACK": [(0, 0, 0, 180, 255, 50)],
    "BROWN": [(10, 50, 30, 25, 200, 150)],
    "BLONDE": [(15, 40, 150, 35, 200, 255)],
    "GRAY/WHITE": [(0, 0, 160, 180, 40, 255)],
}

# Clothing dominant color detection using HSV ranges
CLOTHING_COLORS = {
    "RED": [(0, 100, 80, 10, 255, 255), (160, 100, 80, 180, 255, 255)],
    "BLUE": [(100, 50, 50, 130, 255, 255)],
    "GREEN": [(35, 50, 50, 85, 255, 255)],
    "YELLOW": [(20, 100, 100, 35, 255, 255)],
    "BLACK": [(0, 0, 0, 180, 255, 45)],
    "WHITE": [(0, 0, 200, 180, 30, 255)],
    "GRAY": [(0, 0, 46, 180, 40, 200)],
}


@dataclass
class PersonAttributes:
    """
    Estimated visual attributes for a single detected person.

    All attributes are approximate CV estimates and may be inaccurate.
    """
    hair_color: str = "UNKNOWN"
    clothing_color: str = "UNKNOWN"
    hair_confidence: float = 0.0
    clothing_confidence: float = 0.0


def estimate_person_attributes(
    image: np.ndarray,
    detection: Detection,
) -> PersonAttributes:
    """
    Estimate visual attributes for a single detected person.

    Analyzes different regions of the person crop:
    - Top 25%: Hair color estimation
    - Bottom 60%: Clothing color estimation

    Args:
        image: Full image (BGR).
        detection: Detection object with bounding box.

    Returns:
        PersonAttributes with estimated hair color and clothing color.
    """
    x1, y1, x2, y2 = detection.bbox
    h, w = image.shape[:2]

    # Clamp bounding box to image boundaries
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    crop = image[y1:y2, x1:x2]

    if crop.size == 0 or crop.shape[0] < 10 or crop.shape[1] < 10:
        return PersonAttributes()

    crop_h, _crop_w = crop.shape[:2]

    # ── Hair Color (top 25% of person crop) ──────────────────────────────
    hair_region = crop[0:int(crop_h * 0.25), :]
    hair_color, hair_conf = _estimate_color(hair_region, HAIR_COLORS)

    # ── Clothing Color (bottom 60% of person crop) ───────────────────────
    clothing_region = crop[int(crop_h * 0.4):, :]
    clothing_color, clothing_conf = _estimate_color(clothing_region, CLOTHING_COLORS)

    return PersonAttributes(
        hair_color=hair_color,
        clothing_color=clothing_color,
        hair_confidence=hair_conf,
        clothing_confidence=clothing_conf,
    )


def estimate_all_attributes(
    image: np.ndarray,
    detections: list[Detection],
) -> list[PersonAttributes]:
    """
    Estimate visual attributes for all detected people.

    Args:
        image: Full image (BGR).
        detections: List of Detection objects.

    Returns:
        List of PersonAttributes, one per detection.
    """
    return [estimate_person_attributes(image, det) for det in detections]


def analyze_person_attributes(
    image: np.ndarray,
    bbox_or_detection: Any,
) -> dict[str, Any]:
    """
    Analyze visual attributes for a single person crop.
    Accepts either a Detection object, a dictionary, or a bbox tuple/list (x1, y1, x2, y2).
    """
    if hasattr(bbox_or_detection, "bbox"):
        det = bbox_or_detection
    elif isinstance(bbox_or_detection, dict) and "box" in bbox_or_detection:
        det = Detection(bbox=tuple(bbox_or_detection["box"]), confidence=1.0)
    elif isinstance(bbox_or_detection, dict) and "bbox" in bbox_or_detection:
        det = Detection(bbox=tuple(bbox_or_detection["bbox"]), confidence=1.0)
    elif isinstance(bbox_or_detection, (list, tuple)) and len(bbox_or_detection) >= 4:
        det = Detection(bbox=tuple(bbox_or_detection[:4]), confidence=1.0)
    else:
        return {"hair_color": "UNKNOWN", "clothing_color": "UNKNOWN", "apparent_sex": "UNKNOWN"}

    attrs = estimate_person_attributes(image, det)
    return {
        "hair_color": attrs.hair_color,
        "clothing_color": attrs.clothing_color,
        "hair_confidence": attrs.hair_confidence,
        "clothing_confidence": attrs.clothing_confidence,
        "apparent_sex": "UNKNOWN",
    }


def get_attribute_summary(attributes: list[PersonAttributes]) -> dict:
    """
    Aggregate attribute statistics across all detected people.

    Returns:
        Dictionary with counts for each hair color and clothing color.
    """
    if not attributes:
        return {"hair_colors": {}, "clothing_colors": {}}

    hair_counts: dict[str, int] = {}
    clothing_counts: dict[str, int] = {}

    for attr in attributes:
        hair_counts[attr.hair_color] = hair_counts.get(attr.hair_color, 0) + 1
        clothing_counts[attr.clothing_color] = clothing_counts.get(attr.clothing_color, 0) + 1

    return {
        "hair_colors": dict(sorted(hair_counts.items(), key=lambda x: -x[1])),
        "clothing_colors": dict(sorted(clothing_counts.items(), key=lambda x: -x[1])),
    }


def _estimate_color(
    region: np.ndarray,
    color_map: dict[str, list[tuple]],
) -> tuple[str, float]:
    """
    Estimate the dominant color in a region using HSV color-space analysis.

    Compares the region against predefined HSV ranges for each color category
    and returns the category with the highest pixel coverage.

    Args:
        region: Image region (BGR).
        color_map: Dictionary mapping color names to HSV ranges.

    Returns:
        Tuple of (color_name, confidence).
    """
    if region.size == 0 or region.shape[0] < 5 or region.shape[1] < 5:
        return "UNKNOWN", 0.0

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    total_pixels = hsv.shape[0] * hsv.shape[1]

    best_color = "OTHER"
    best_ratio = 0.0

    for color_name, ranges in color_map.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (h_lo, s_lo, v_lo, h_hi, s_hi, v_hi) in ranges:
            lower = np.array([h_lo, s_lo, v_lo])
            upper = np.array([h_hi, s_hi, v_hi])
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        ratio = np.sum(mask > 0) / total_pixels
        if ratio > best_ratio:
            best_ratio = ratio
            best_color = color_name

    # If the best match covers less than 15% of pixels, label as UNKNOWN
    if best_ratio < 0.15:
        return "UNKNOWN", best_ratio

    return best_color, best_ratio
