import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from computer_vision.person_detection import Detection
from computer_vision.tracking import CentroidTracker


class TestCentroidTracker(unittest.TestCase):
    def setUp(self):
        # Tracker with 0.1 max_distance_ratio
        self.tracker = CentroidTracker(max_disappeared=5, max_distance_ratio=0.1)
        self.frame_shape = (1000, 1000) # Diagonal is ~1414, threshold is ~141.4

    def test_new_detections(self):
        det1 = Detection(bbox=(10, 10, 50, 50), confidence=0.9)
        det2 = Detection(bbox=(200, 200, 250, 250), confidence=0.9)
        
        updated = self.tracker.update([det1, det2], self.frame_shape)
        self.assertEqual(len(updated), 2)
        
        # New objects get ID 1 and 2
        ids = {d.person_id for d in updated}
        self.assertEqual(ids, {1, 2})

    def test_matching_existing_detections(self):
        # Frame 1
        det1 = Detection(bbox=(10, 10, 50, 50), confidence=0.9)
        self.tracker.update([det1], self.frame_shape)
        
        # Frame 2 (moved slightly, within 141.4 threshold)
        det1_new = Detection(bbox=(20, 20, 60, 60), confidence=0.9)
        updated = self.tracker.update([det1_new], self.frame_shape)
        
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0].person_id, 1) # Retains ID 1

    def test_deregister_disappeared(self):
        # Frame 1
        det1 = Detection(bbox=(10, 10, 50, 50), confidence=0.9)
        self.tracker.update([det1], self.frame_shape)
        
        self.assertEqual(self.tracker.active_count, 1)
        
        # Missing for max_disappeared frames
        for _ in range(6):
            self.tracker.update([], self.frame_shape)
            
        self.assertEqual(self.tracker.active_count, 0)

if __name__ == '__main__':
    unittest.main()
