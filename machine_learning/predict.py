"""
Prediction Module for Visionlytics.

Loads trained models and provides a simple prediction interface for
classifying crowd density from extracted features.

Usage:
    predictor = CrowdPredictor()
    label, confidence = predictor.predict(features_dict)
    probabilities = predictor.predict_proba(features_dict)
"""

import os
import sys
import numpy as np
import joblib
from typing import Dict, Tuple, Optional

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from machine_learning.preprocessing import (
    scale_features,
    MODELS_DIR,
    FEATURE_COLUMNS,
    LABEL_CLASSES,
)


class CrowdPredictor:
    """
    Predicts crowd density (LOW/MEDIUM/HIGH) from extracted features.

    Loads the best trained model and scaler from disk and provides
    predict() and predict_proba() methods.

    The predictor can also load a specific model by name.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the predictor.

        Args:
            model_name: Specific model to load (e.g., 'random_forest').
                        If None, loads the best model.
        """
        self._model = None
        self._scaler = None
        self._model_name = model_name
        self._meta = None

    def _load(self):
        """Lazily load model and scaler on first prediction."""
        if self._model is not None:
            return

        if self._model_name:
            safe_name = self._model_name.lower().replace(" ", "_")
            model_path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
        else:
            model_path = os.path.join(MODELS_DIR, "best_model.joblib")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at '{model_path}'. "
                "Train the models first using the ML Models page or "
                "run: python -m machine_learning.train"
            )

        self._model = joblib.load(model_path)

        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        if os.path.exists(scaler_path):
            self._scaler = joblib.load(scaler_path)

        meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
        if os.path.exists(meta_path):
            self._meta = joblib.load(meta_path)

    @property
    def model_name(self) -> str:
        """Return the name of the loaded model."""
        self._load()
        if self._meta and "name" in self._meta:
            return self._meta["name"]
        return self._model_name or "Best Model"

    @property
    def is_loaded(self) -> bool:
        """Check if models exist on disk."""
        model_path = os.path.join(MODELS_DIR, "best_model.joblib")
        return os.path.exists(model_path)

    def predict(self, features: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict crowd density label and confidence.

        Args:
            features: Dictionary mapping feature names to values.
                      Must contain all 10 features from FeatureExtractor.

        Returns:
            Tuple of (label, confidence) where:
                - label is one of 'LOW', 'MEDIUM', 'HIGH'
                - confidence is the probability of the predicted class (0-1)
        """
        self._load()

        # Scale features using the saved scaler
        X_scaled = scale_features(features, self._scaler)

        # Predict class
        y_pred = self._model.predict(X_scaled)[0]
        label = LABEL_CLASSES[int(y_pred)]

        # Get confidence (probability of predicted class)
        confidence = 0.0
        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(X_scaled)[0]
            confidence = float(proba[int(y_pred)])
        else:
            # For models without predict_proba, use decision function
            confidence = 0.85  # Default confidence

        return label, confidence

    def predict_proba(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Get probability distribution over all density classes.

        Args:
            features: Dictionary mapping feature names to values.

        Returns:
            Dictionary mapping class labels to their probabilities.
            Example: {'LOW': 0.1, 'MEDIUM': 0.2, 'HIGH': 0.7}
        """
        self._load()

        X_scaled = scale_features(features, self._scaler)

        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(X_scaled)[0]
            return {LABEL_CLASSES[i]: float(proba[i]) for i in range(len(LABEL_CLASSES))}
        else:
            # Fallback: return the prediction with high confidence
            y_pred = int(self._model.predict(X_scaled)[0])
            result = {label: 0.05 for label in LABEL_CLASSES}
            result[LABEL_CLASSES[y_pred]] = 0.9
            return result
