"""
Model Evaluation Module for Visionlytics.

Provides comprehensive evaluation metrics for crowd density classifiers.
Computes accuracy, precision, recall, F1-score, and confusion matrices.

ML Concepts Demonstrated:
    - Accuracy: Fraction of correct predictions (can be misleading with
      imbalanced classes).
    - Precision: Of all predictions for a class, how many were correct?
      (penalizes false positives)
    - Recall: Of all actual instances of a class, how many did we find?
      (penalizes false negatives)
    - F1-Score: Harmonic mean of precision and recall — balances both.
    - Confusion Matrix: Shows exactly where the model makes mistakes
      (which classes get confused with which).
    - Feature Importance: For tree-based models, shows which features
      contribute most to the decision.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: List[str],
) -> Dict:
    """
    Evaluate a trained model on a test/validation set.

    Computes comprehensive classification metrics.

    Args:
        model: Trained scikit-learn classifier.
        X_test: Test feature matrix.
        y_test: True test labels (encoded as integers).
        class_names: List of class label strings ['LOW', 'MEDIUM', 'HIGH'].

    Returns:
        Dictionary containing:
            - accuracy: Overall accuracy (fraction correct)
            - precision_per_class: Precision for each class
            - recall_per_class: Recall for each class
            - f1_per_class: F1-score for each class
            - precision_weighted: Weighted average precision
            - recall_weighted: Weighted average recall
            - f1_weighted: Weighted average F1-score
            - confusion_matrix: 3x3 confusion matrix as list of lists
            - classification_report: Full text classification report
            - feature_importance: Feature importances (if available)
    """
    y_pred = model.predict(X_test)

    # ── Overall Metrics ──────────────────────────────────────────────────
    acc = accuracy_score(y_test, y_pred)

    # ── Per-Class Metrics ────────────────────────────────────────────────
    precision_per = precision_score(y_test, y_pred, average=None, zero_division=0)
    recall_per = recall_score(y_test, y_pred, average=None, zero_division=0)
    f1_per = f1_score(y_test, y_pred, average=None, zero_division=0)

    # ── Weighted Averages ────────────────────────────────────────────────
    precision_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # ── Confusion Matrix ─────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)

    # ── Classification Report ────────────────────────────────────────────
    report = classification_report(
        y_test, y_pred,
        target_names=class_names,
        zero_division=0,
    )

    # ── Feature Importance (tree-based models) ───────────────────────────
    feature_importance = None
    if hasattr(model, "feature_importances_"):
        feature_importance = model.feature_importances_.tolist()
    elif hasattr(model, "coef_"):
        # For logistic regression, use absolute coefficient values
        feature_importance = np.abs(model.coef_).mean(axis=0).tolist()

    return {
        "accuracy": round(float(acc), 4),
        "precision_per_class": {
            class_names[i]: round(float(precision_per[i]), 4)
            for i in range(len(class_names))
        },
        "recall_per_class": {
            class_names[i]: round(float(recall_per[i]), 4)
            for i in range(len(class_names))
        },
        "f1_per_class": {
            class_names[i]: round(float(f1_per[i]), 4)
            for i in range(len(class_names))
        },
        "precision_weighted": round(float(precision_w), 4),
        "recall_weighted": round(float(recall_w), 4),
        "f1_weighted": round(float(f1_w), 4),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "feature_importance": feature_importance,
    }


def compare_models(
    models: Dict[str, Any],
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: List[str],
) -> pd.DataFrame:
    """
    Compare all models and return a summary DataFrame.

    Args:
        models: Dictionary of model_name → trained model.
        X_test: Test feature matrix.
        y_test: True test labels.
        class_names: List of class label strings.

    Returns:
        DataFrame with columns: Model, Accuracy, Precision, Recall, F1-Score,
        sorted by F1-Score descending.
    """
    rows = []
    for name, model in models.items():
        metrics = evaluate_model(model, X_test, y_test, class_names)
        rows.append({
            "Model": name,
            "Accuracy": metrics["accuracy"],
            "Precision": metrics["precision_weighted"],
            "Recall": metrics["recall_weighted"],
            "F1-Score": metrics["f1_weighted"],
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("F1-Score", ascending=False).reset_index(drop=True)

    return df


def get_feature_importance_df(
    model: Any,
    feature_names: List[str],
) -> Optional[pd.DataFrame]:
    """
    Extract feature importances from a model and return as a DataFrame.

    Works with tree-based models (feature_importances_) and linear models
    (coef_).

    Args:
        model: Trained scikit-learn model.
        feature_names: List of feature column names.

    Returns:
        DataFrame with columns: Feature, Importance, sorted descending.
        Returns None if the model doesn't support feature importances.
    """
    importances = None

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).mean(axis=0)

    if importances is None:
        return None

    df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances,
    })
    df = df.sort_values("Importance", ascending=False).reset_index(drop=True)

    return df
