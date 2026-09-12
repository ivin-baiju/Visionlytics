"""
Centroid Tracking Module for Visionlytics.

Implements a simple centroid-based tracker for maintaining person identity
across video frames. This tracker assigns unique IDs to detections and
matches them between frames using Euclidean distance between centroids.

Algorithm:
    1. For each new frame, compute centroids of all detections.
    2. Match new centroids to existing tracked objects using minimum distance.
    3. Assign existing IDs to matched detections.
    4. Register new IDs for unmatched detections.
    5. Deregister objects that have been missing for too many frames.

This is a lightweight tracker suitable for a student project — it does not
use complex methods like Kalman filters or deep association.
"""

import numpy as np
from collections import OrderedDict
from typing import List, Tuple, Dict
from scipy.spatial.distance import cdist

from computer_vision.person_detection import Detection


class CentroidTracker:
    """
    Tracks detected people across video frames using centroid matching.

    Parameters:
        max_disappeared: Number of consecutive frames an object can be
                         missing before it is deregistered. Default is 30.
        max_distance_ratio: Maximum distance (as a fraction of the frame diagonal)
                      for a centroid match. If the closest centroid is farther
                      than this, the detection is registered as a new object.
                      Default is 0.05 (5% of diagonal).
    """

    def __init__(self, max_disappeared: int = 30, max_distance_ratio: float = 0.05):
        self.max_disappeared = max_disappeared
        self.max_distance_ratio = max_distance_ratio
        self._next_id = 1
        self._objects: OrderedDict[int, np.ndarray] = OrderedDict()
        self._disappeared: OrderedDict[int, int] = OrderedDict()
        self._total_unique = 0  # Total unique people seen across all frames

    @property
    def total_unique_people(self) -> int:
        """Total number of unique people tracked since initialization."""
        return self._total_unique

    @property
    def active_count(self) -> int:
        """Number of currently tracked (active) people."""
        return len(self._objects)

    def reset(self):
        """Reset the tracker state."""
        self._next_id = 1
        self._objects.clear()
        self._disappeared.clear()
        self._total_unique = 0

    def update(self, detections: List[Detection], frame_shape: Tuple[int, int]) -> List[Detection]:
        """
        Update tracker with new detections and assign person IDs.

        Args:
            detections: List of Detection objects from the current frame.
            frame_shape: Tuple of (height, width) of the current frame.

        Returns:
            Updated list of Detection objects with person_id assigned.
        """
        # If no detections, mark all existing objects as disappeared
        if len(detections) == 0:
            for obj_id in list(self._disappeared.keys()):
                self._disappeared[obj_id] += 1
                if self._disappeared[obj_id] > self.max_disappeared:
                    self._deregister(obj_id)
            return []

        # Compute centroids for current detections
        input_centroids = np.array([det.center for det in detections])

        # If we have no existing objects, register all detections
        if len(self._objects) == 0:
            for i, det in enumerate(detections):
                det.person_id = self._register(input_centroids[i])
            return detections

        # Match existing objects to new detections using distance matrix
        object_ids = list(self._objects.keys())
        object_centroids = np.array(list(self._objects.values()))

        # Compute distance matrix between all existing and new centroids
        dist_matrix = cdist(object_centroids, input_centroids)

        # Find best matches (Hungarian-style greedy matching)
        rows = dist_matrix.min(axis=1).argsort()
        cols = dist_matrix.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        frame_diagonal = np.sqrt(frame_shape[0]**2 + frame_shape[1]**2)
        pixel_max_dist = self.max_distance_ratio * frame_diagonal

        for (row, col) in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            # Only match if distance is within threshold
            if dist_matrix[row, col] > pixel_max_dist:
                continue

            obj_id = object_ids[row]
            self._objects[obj_id] = input_centroids[col]
            self._disappeared[obj_id] = 0
            detections[col].person_id = obj_id

            used_rows.add(row)
            used_cols.add(col)

        # Handle unmatched existing objects (they disappeared)
        for row in range(len(object_ids)):
            if row not in used_rows:
                obj_id = object_ids[row]
                self._disappeared[obj_id] += 1
                if self._disappeared[obj_id] > self.max_disappeared:
                    self._deregister(obj_id)

        # Handle unmatched new detections (register as new)
        for col in range(len(detections)):
            if col not in used_cols:
                detections[col].person_id = self._register(input_centroids[col])

        return detections

    def _register(self, centroid: np.ndarray) -> int:
        """Register a new object and return its ID."""
        obj_id = self._next_id
        self._objects[obj_id] = centroid
        self._disappeared[obj_id] = 0
        self._next_id += 1
        self._total_unique += 1
        return obj_id

    def _deregister(self, obj_id: int):
        """Remove an object that has disappeared for too long."""
        del self._objects[obj_id]
        del self._disappeared[obj_id]
