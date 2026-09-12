"""
Heatmap Generation Module for Visionlytics.

Creates crowd density heatmaps by placing Gaussian blobs at person center
positions. The heatmap is overlaid on the original image to visualize
areas of high crowd concentration.

Color mapping:
    Green  → Low concentration
    Yellow → Medium concentration
    Red    → High concentration
"""

import cv2
import numpy as np
from typing import List

from computer_vision.person_detection import Detection


def generate_heatmap(
    image: np.ndarray,
    detections: List[Detection],
    intensity: float = 0.6,
    radius: int = 80,
) -> np.ndarray:
    """
    Generate a crowd density heatmap overlaid on the image.

    Each detected person contributes a Gaussian blob centered at their
    bounding box center. Overlapping blobs accumulate to show crowded areas.

    Args:
        image: Original image (BGR, from OpenCV).
        detections: List of Detection objects.
        intensity: Blend factor for the heatmap overlay (0 = invisible, 1 = opaque).
        radius: Radius of each Gaussian blob in pixels. Larger radius creates
                smoother, more spread-out heatmaps.

    Returns:
        Image with heatmap overlay (BGR, same size as input).
    """
    h, w = image.shape[:2]

    # Create a blank accumulation map
    heat = np.zeros((h, w), dtype=np.float32)

    if len(detections) == 0:
        # No detections — return original image
        return image.copy()

    # Place single-pixel impulses for each detection
    for det in detections:
        cx, cy = int(det.center[0]), int(det.center[1])
        if 0 <= cx < w and 0 <= cy < h:
            # We can scale the weight by bounding box size if desired,
            # but a simple +1 impulse is fastest.
            heat[cy, cx] += 1.0

    # Apply a single large Gaussian blur to spread the impulses
    ksize = int(radius * 2)
    if ksize % 2 == 0:
        ksize += 1
    
    heat = cv2.GaussianBlur(heat, (ksize, ksize), 0)

    # Normalize heatmap to [0, 255]
    if heat.max() > 0:
        heat = (heat / heat.max() * 255).astype(np.uint8)
    else:
        heat = heat.astype(np.uint8)

    # Apply colormap: COLORMAP_JET gives green → yellow → red
    heatmap_colored = cv2.applyColorMap(heat, cv2.COLORMAP_JET)

    # Blend the heatmap with the original image
    # Where heat is low (blue areas), reduce the blend factor
    mask = heat.astype(np.float32) / 255.0
    mask = np.stack([mask] * 3, axis=-1)  # Convert to 3-channel

    blended = image.astype(np.float32) * (1 - mask * intensity) + \
              heatmap_colored.astype(np.float32) * (mask * intensity)
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    return blended


def generate_standalone_heatmap(
    width: int,
    height: int,
    detections: List[Detection],
    radius: int = 80,
) -> np.ndarray:
    """
    Generate a standalone heatmap image (without the original image underneath).

    Useful for displaying the heatmap as a separate visualization.

    Args:
        width: Image width.
        height: Image height.
        detections: List of Detection objects.
        radius: Gaussian blob radius.

    Returns:
        Heatmap image (BGR).
    """
    # Create a dark background
    bg = np.zeros((height, width, 3), dtype=np.uint8) + 20
    return generate_heatmap(bg, detections, intensity=0.9, radius=radius)
