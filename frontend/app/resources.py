"""
Shared Cached Resources for Visionlytics.

Provides @st.cache_resource-wrapped singletons for the YOLO detector,
feature extractor, and ML predictor so that every UI page reuses the
same in-memory instances instead of reloading from disk on every click.

Usage (in any UI page):
    from app.resources import get_detector, get_extractor, get_predictor
    detector  = get_detector(confidence_threshold=0.3)
    extractor = get_extractor()
    predictor = get_predictor()
"""

import streamlit as st


@st.cache_resource
def get_detector(confidence_threshold: float = 0.3):
    """Load person detector once and cache across sessions."""
    from computer_vision.person_detection import PersonDetector
    return PersonDetector(confidence_threshold=confidence_threshold)


@st.cache_resource
def get_extractor():
    """Load feature extractor once and cache across sessions."""
    from computer_vision.feature_extraction import FeatureExtractor
    return FeatureExtractor()


@st.cache_resource
def get_predictor():
    """Load ML predictor once and cache across sessions."""
    from machine_learning.predict import CrowdPredictor
    predictor = CrowdPredictor()
    if predictor.is_loaded:
        return predictor
    return None
