"""
Feature Extraction Module for Visionlytics.

Extracts 10 numerical features from person detections in an image/frame.
These features form the input to the statistical ML classifiers for
crowd density prediction (LOW / MEDIUM / HIGH).

Feature List:
    1. people_count          — Number of detected people
    2. occupancy_ratio       — Fraction of frame area covered by bounding boxes
    3. avg_person_area       — Mean bounding box area as fraction of frame area
    4. avg_distance          — Mean pairwise Euclidean distance between person centers (normalized)
    5. min_distance          — Minimum pairwise distance (normalized)
    6. spatial_spread        — Standard deviation of person positions (normalized)
    7. top_region_count      — Number of people in top third of frame
    8. middle_region_count   — Number of people in middle third
    9. bottom_region_count   — Number of people in bottom third
   10. frame_occupancy_density — people_count normalized by frame area (in thousands of pixels)

The normalization is done relative to the frame diagonal so that features
are comparable across different image resolutions.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from scipy.spatial.distance import pdist

from computer_vision.person_detection import Detection


class FeatureExtractor:
    """
    Extracts crowd-related features from a list of person detections.

    Usage:
        extractor = FeatureExtractor()
        features = extractor.extract(detections, frame_width=1920, frame_height=1080)
        # or
        features = extractor.extract(detections, (1080, 1920))
        # features is a dict with 10 numerical values
    """

    # Names of all features (used as column headers in the dataset)
    FEATURE_NAMES = [
        "people_count",
        "occupancy_ratio",
        "avg_person_area",
        "avg_distance",
        "min_distance",
        "spatial_spread",
        "top_region_count",
        "middle_region_count",
        "bottom_region_count",
        "frame_occupancy_density",
    ]

    def extract(
        self,
        detections: List[Detection],
        frame_width: Union[int, Tuple[int, int], List[int]],
        frame_height: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Extract all 10 features from a set of detections.

        Args:
            detections: List of Detection objects from PersonDetector.
            frame_width: Width of the image in pixels, or a shape tuple/list (height, width).
            frame_height: Height of the image in pixels (if frame_width is width).

        Returns:
            Dictionary mapping feature names to their computed values.
        """
        if isinstance(frame_width, (tuple, list)):
            # Passed as (height, width) or (h, w)
            if len(frame_width) >= 2:
                frame_height, frame_width = int(frame_width[0]), int(frame_width[1])
            else:
                frame_width = int(frame_width[0])
                frame_height = frame_width

        if frame_height is None:
            frame_height = int(frame_width)
        else:
            frame_width = int(frame_width)
            frame_height = int(frame_height)

        frame_area = max(1, frame_width * frame_height)
        # Diagonal length used to normalize distances
        frame_diagonal = np.sqrt(frame_width**2 + frame_height**2)

        n = len(detections)

        # ── Feature 1: People Count ──────────────────────────────────────
        people_count = n

        if n == 0:
            # No people detected — return zeros for all features
            return {name: 0.0 for name in self.FEATURE_NAMES}

        # Collect centers and areas
        centers = np.array([det.center for det in detections])  # shape (n, 2)
        areas = np.array([det.area for det in detections])       # shape (n,)

        # ── Feature 2: Occupancy Ratio ───────────────────────────────────
        # Fraction of frame area covered by all bounding boxes (may overlap)
        total_bbox_area = sum(areas)
        occupancy_ratio = min(total_bbox_area / frame_area, 1.0)

        # ── Feature 3: Average Person Area ───────────────────────────────
        # Mean bounding box area as a fraction of the total frame area
        avg_person_area = float(np.mean(areas)) / frame_area

        # ── Features 4 & 5: Average and Minimum Pairwise Distance ───────
        if n >= 2:
            # pdist computes all pairwise Euclidean distances
            pairwise_distances = pdist(centers, metric="euclidean")
            # Normalize by frame diagonal so values are in [0, 1]
            normalized_distances = pairwise_distances / frame_diagonal
            avg_distance = float(np.mean(normalized_distances))
            min_distance = float(np.min(normalized_distances))
        else:
            # Only one person — set distances to maximum (1.0)
            avg_distance = 1.0
            min_distance = 1.0

        # ── Feature 6: Spatial Spread ────────────────────────────────────
        # Standard deviation of person center positions (normalized)
        # High spread → people are spread out; low spread → clustered
        if n >= 2:
            std_x = np.std(centers[:, 0]) / frame_width
            std_y = np.std(centers[:, 1]) / frame_height
            spatial_spread = float(np.sqrt(std_x**2 + std_y**2))
        else:
            spatial_spread = 0.0

        # ── Features 7–9: Regional Counts ────────────────────────────────
        # Divide frame into top, middle, bottom thirds
        third_h = frame_height / 3
        top_region_count = 0
        middle_region_count = 0
        bottom_region_count = 0

        for det in detections:
            cy = det.center[1]
            if cy < third_h:
                top_region_count += 1
            elif cy < 2 * third_h:
                middle_region_count += 1
            else:
                bottom_region_count += 1

        # ── Feature 10: Frame Occupancy Density ──────────────────────────
        # People count normalized by frame area (per 1000x1000 pixel block)
        frame_occupancy_density = people_count / (frame_area / 1_000_000)

        return {
            "people_count": float(people_count),
            "occupancy_ratio": round(occupancy_ratio, 6),
            "avg_person_area": round(avg_person_area, 6),
            "avg_distance": round(avg_distance, 6),
            "min_distance": round(min_distance, 6),
            "spatial_spread": round(spatial_spread, 6),
            "top_region_count": float(top_region_count),
            "middle_region_count": float(middle_region_count),
            "bottom_region_count": float(bottom_region_count),
            "frame_occupancy_density": round(frame_occupancy_density, 6),
        }

    @staticmethod
    def features_to_display(features: Dict[str, float]) -> Dict[str, str]:
        """
        Format extracted features as human-readable strings for UI display.

        Args:
            features: Dictionary of raw feature values.

        Returns:
            Dictionary of formatted display strings.
        """
        return {
            "People Detected": f"{int(features['people_count'])}",
            "Occupancy": f"{features['occupancy_ratio'] * 100:.1f}%",
            "Avg Person Area": f"{features['avg_person_area'] * 100:.2f}%",
            "Avg Distance": f"{features['avg_distance']:.3f}",
            "Min Distance": f"{features['min_distance']:.3f}",
            "Spatial Spread": f"{features['spatial_spread']:.3f}",
            "Top Region": f"{int(features['top_region_count'])}",
            "Middle Region": f"{int(features['middle_region_count'])}",
            "Bottom Region": f"{int(features['bottom_region_count'])}",
            "Density Score": f"{features['frame_occupancy_density']:.2f}",
        }
