"""
Feature Extraction Module for Visionlytics.

Extracts 10 numerical features from person detections in an image/frame.
These features form the input to the statistical ML classifiers for
crowd density prediction (LOW / MEDIUM / HIGH).

Performance Notes:
    - Occupancy ratio is computed analytically (no full-resolution pixel mask)
    - Pairwise distances use vectorized NumPy operations
    - All features computed in a single pass over detections

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

from computer_vision.person_detection import Detection


def _compute_union_area(boxes: np.ndarray, frame_w: int, frame_h: int) -> int:
    """Compute the pixel-area union of axis-aligned bounding boxes analytically.

    Uses a sweep-line algorithm on the Y-axis with an interval-union on the
    X-axis.  For typical crowd counts (< 200 boxes) this is dramatically faster
    than allocating a full-resolution boolean mask (which can be 8+ MB for 4K).

    Args:
        boxes: (N, 4) array of [x1, y1, x2, y2] clipped to frame bounds.
        frame_w: Frame width in pixels.
        frame_h: Frame height in pixels.

    Returns:
        Total number of unique pixels covered by at least one box.
    """
    n = len(boxes)
    if n == 0:
        return 0

    # For very few boxes the simple inclusion-exclusion via a small mask is fine
    # and avoids the sweep-line overhead.  The threshold is chosen so that the
    # mask allocation stays under ~1 MB.
    total_box_pixels = int(np.sum((boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])))
    if total_box_pixels == 0:
        return 0

    # ── Fast path: single box ────────────────────────────────────────────
    if n == 1:
        x1, y1, x2, y2 = boxes[0]
        return int((x2 - x1) * (y2 - y1))

    # ── Fast path: if frame is small enough, use a mask ──────────────────
    if frame_w * frame_h < 1_000_000:  # < 1 MP
        mask = np.zeros((frame_h, frame_w), dtype=np.uint8)
        for i in range(n):
            x1, y1, x2, y2 = boxes[i]
            mask[y1:y2, x1:x2] = 1
        return int(np.count_nonzero(mask))

    # ── General path: coordinate-compression sweep ───────────────────────
    # Collect all unique Y coordinates (events)
    y_coords = np.unique(np.concatenate([boxes[:, 1], boxes[:, 3]]))
    y_coords = np.clip(y_coords, 0, frame_h)
    y_coords = np.unique(y_coords)

    union_area = 0
    for k in range(len(y_coords) - 1):
        y_lo = int(y_coords[k])
        y_hi = int(y_coords[k + 1])
        band_height = y_hi - y_lo
        if band_height <= 0:
            continue

        # Find boxes that overlap this Y band
        active = (boxes[:, 1] < y_hi) & (boxes[:, 3] > y_lo)
        if not np.any(active):
            continue

        # Compute union of X intervals for active boxes
        x_intervals = boxes[active][:, [0, 2]].astype(int)
        x_intervals = x_intervals[x_intervals[:, 0] < x_intervals[:, 1]]
        if len(x_intervals) == 0:
            continue

        # Sort by start
        order = np.argsort(x_intervals[:, 0])
        x_intervals = x_intervals[order]

        # Merge overlapping intervals
        x_union = 0
        cur_start, cur_end = x_intervals[0]
        for j in range(1, len(x_intervals)):
            s, e = x_intervals[j]
            if s <= cur_end:
                cur_end = max(cur_end, e)
            else:
                x_union += cur_end - cur_start
                cur_start, cur_end = s, e
        x_union += cur_end - cur_start

        union_area += x_union * band_height

    return union_area


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
        detections: list[Detection],
        frame_width: int | tuple[int, int] | list[int],
        frame_height: int | None = None,
    ) -> dict[str, float]:
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

        # ── Vectorized extraction of centers, areas, bboxes ──────────────
        bboxes = np.array([det.bbox for det in detections], dtype=np.int32)
        centers = np.column_stack([
            (bboxes[:, 0] + bboxes[:, 2]) / 2.0,
            (bboxes[:, 1] + bboxes[:, 3]) / 2.0,
        ])
        widths = np.maximum(0, bboxes[:, 2] - bboxes[:, 0])
        heights = np.maximum(0, bboxes[:, 3] - bboxes[:, 1])
        areas = widths * heights

        # ── Feature 2: Occupancy Ratio (ANALYTIC — no pixel mask) ────────
        # Clip bboxes to frame bounds for union-area computation
        clipped = bboxes.copy()
        clipped[:, 0] = np.clip(clipped[:, 0], 0, frame_width)
        clipped[:, 1] = np.clip(clipped[:, 1], 0, frame_height)
        clipped[:, 2] = np.clip(clipped[:, 2], 0, frame_width)
        clipped[:, 3] = np.clip(clipped[:, 3], 0, frame_height)

        covered_area = _compute_union_area(clipped, frame_width, frame_height)
        occupancy_ratio = covered_area / frame_area

        # ── Feature 3: Average Person Area ───────────────────────────────
        avg_person_area = float(np.mean(areas)) / frame_area

        # ── Features 4 & 5: Vectorized pairwise distances ───────────────
        if n >= 2:
            # Compute pairwise distances using broadcasting (faster than pdist for small N)
            diff = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
            dist_matrix = np.sqrt(np.sum(diff**2, axis=2))
            # Extract upper triangle (no self-pairs)
            triu_indices = np.triu_indices(n, k=1)
            pairwise_distances = dist_matrix[triu_indices]
            # Normalize by frame diagonal so values are in [0, 1]
            normalized_distances = pairwise_distances / frame_diagonal
            avg_distance = float(np.mean(normalized_distances))
            min_distance = float(np.min(normalized_distances))
        else:
            avg_distance = 1.0
            min_distance = 1.0

        # ── Feature 6: Spatial Spread ────────────────────────────────────
        if n >= 2:
            std_x = np.std(centers[:, 0]) / frame_width
            std_y = np.std(centers[:, 1]) / frame_height
            spatial_spread = float(np.sqrt(std_x**2 + std_y**2))
        else:
            spatial_spread = 0.0

        # ── Features 7–9: Regional Counts (vectorized) ───────────────────
        third_h = frame_height / 3.0
        cy_values = centers[:, 1]

        top_region_count = int(np.sum(cy_values < third_h))
        middle_region_count = int(np.sum((cy_values >= third_h) & (cy_values < 2 * third_h)))
        bottom_region_count = int(np.sum(cy_values >= 2 * third_h))

        # ── Feature 10: Frame Occupancy Density (vectorized) ─────────────
        # Perspective weighting: people near the top are further away
        depth_weights = 1.0 + 3.0 * (1.0 - (cy_values / frame_height))
        weighted_people_count = float(np.sum(depth_weights))
        frame_occupancy_density = weighted_people_count / (frame_area / 1_000_000)

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
    def features_to_display(features: dict[str, float]) -> dict[str, str]:
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
