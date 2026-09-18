"""
Model Training Module for Visionlytics.

Trains all ML models on the crowd density dataset and saves the trained
models to disk. Also identifies the best-performing model based on
validation accuracy.

Training Pipeline:
    1. Load and preprocess the dataset
    2. Split into train/validation/test sets
    3. Train each model on the training set
    4. Evaluate each model on the validation set
    5. Select the best model by F1-score
    6. Save all models and the best model to disk

All models are serialized using joblib for fast loading during prediction.
"""

import os
import sys
import time

import joblib
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from machine_learning.evaluation import evaluate_model
from machine_learning.models import get_models
from machine_learning.preprocessing import (
    FEATURE_COLUMNS,
    LABEL_CLASSES,
    MODELS_DIR,
    load_dataset,
    preprocess_and_split,
)


def train_all_models(
    dataset_path: str | None = None,
    verbose: bool = True,
) -> dict:
    """
    Train all ML models on the crowd density dataset.

    This is the main training function. It:
        1. Loads the dataset from CSV
        2. Preprocesses and splits the data (70/15/15)
        3. Trains each of the 5 models
        4. Evaluates on validation set
        5. Saves all models and selects the best one

    Args:
        dataset_path: Path to the CSV dataset. Uses default if None.
        verbose: Whether to print training progress.

    Returns:
        Dictionary containing:
            - 'models': dict of model_name → trained model
            - 'metrics': dict of model_name → evaluation metrics
            - 'best_model_name': name of the best model
            - 'best_model': the best trained model
            - 'training_times': dict of model_name → training time in seconds
            - 'data_info': dict with dataset split sizes
    """
    if verbose:
        print("=" * 60)
        print("  VISIONLYTICS — Model Training Pipeline")
        print("=" * 60)

    # ── Step 1: Load Dataset ─────────────────────────────────────────────
    if verbose:
        print("\n[1/5] Loading dataset...")

    df = load_dataset(dataset_path)

    if verbose:
        print(f"  → Loaded {len(df)} samples")
        print(f"  → Class distribution: {df['density_label'].value_counts().to_dict()}")

    # ── Step 2: Preprocess and Split ─────────────────────────────────────
    if verbose:
        print("\n[2/5] Preprocessing and splitting data...")

    X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder = \
        preprocess_and_split(df, save_scaler=True)

    data_info = {
        "total_samples": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "n_features": X_train.shape[1],
        "n_classes": len(LABEL_CLASSES),
        "feature_names": FEATURE_COLUMNS,
        "class_names": LABEL_CLASSES,
    }

    if verbose:
        print(f"  → Train: {data_info['train_samples']} samples")
        print(f"  → Validation: {data_info['val_samples']} samples")
        print(f"  → Test: {data_info['test_samples']} samples")
        print(f"  → Features: {data_info['n_features']}")

    # ── Step 3: Train Models ─────────────────────────────────────────────
    if verbose:
        print("\n[3/5] Training models...")

    models = get_models()
    trained_models = {}
    training_times = {}

    for name, model in models.items():
        if verbose:
            print(f"  → Training {name}...", end=" ", flush=True)

        start_time = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start_time

        trained_models[name] = model
        training_times[name] = round(elapsed, 4)

        if verbose:
            print(f"Done ({elapsed:.3f}s)")

    # ── Step 4: Evaluate on Validation Set & Cross-Validation ───────────────────────────────
    if verbose:
        print("\n[4/5] Evaluating models on validation set (with 5-Fold CV)...")

    all_metrics = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in trained_models.items():
        metrics = evaluate_model(model, X_val, y_val, LABEL_CLASSES)
        
        # Calculate CV score on training data for robustness
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted')
        metrics['cv_f1_mean'] = round(float(np.mean(cv_scores)), 4)
        metrics['cv_f1_std'] = round(float(np.std(cv_scores)), 4)
        
        all_metrics[name] = metrics

        if verbose:
            print(f"  → {name}: Val F1={metrics['f1_weighted']:.4f} | "
                  f"CV F1={metrics['cv_f1_mean']:.4f} ± {metrics['cv_f1_std']:.4f}")

    # ── Step 5: Select Best Model and Save ───────────────────────────────
    if verbose:
        print("\n[5/5] Saving models...")

    best_model_name = max(all_metrics, key=lambda k: all_metrics[k]["f1_weighted"])
    best_model = trained_models[best_model_name]

    # Save all models
    os.makedirs(MODELS_DIR, exist_ok=True)
    for name, model in trained_models.items():
        safe_name = name.lower().replace(" ", "_")
        model_path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
        joblib.dump(model, model_path)
        if verbose:
            print(f"  → Saved {name} → {safe_name}.joblib")

    # Save the best model separately for quick loading
    best_path = os.path.join(MODELS_DIR, "best_model.joblib")
    joblib.dump(best_model, best_path)

    # Save metadata about the best model
    meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
    joblib.dump({"name": best_model_name, "metrics": all_metrics[best_model_name]}, meta_path)

    if verbose:
        print(f"\n  ★ Best model: {best_model_name} "
              f"(F1={all_metrics[best_model_name]['f1_weighted']:.4f})")
        print("\n" + "=" * 60)
        print("  Training complete!")
        print("=" * 60)

    # Also evaluate on test set for final reporting
    test_metrics = {}
    for name, model in trained_models.items():
        test_metrics[name] = evaluate_model(model, X_test, y_test, LABEL_CLASSES)

    # Save all evaluation metrics to disk
    results_path = os.path.join(MODELS_DIR, "evaluation_results.joblib")
    joblib.dump({
        "val_metrics": all_metrics,
        "test_metrics": test_metrics,
        "training_times": training_times,
        "best_model_name": best_model_name,
        "data_info": data_info,
    }, results_path)

    return {
        "models": trained_models,
        "val_metrics": all_metrics,
        "test_metrics": test_metrics,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "training_times": training_times,
        "data_info": data_info,
        "scaler": scaler,
        "label_encoder": label_encoder,
    }


def retrain_on_full(
    dataset_path: str | None = None,
    model_name: str | None = None,
) -> dict:
    """
    Retrain a specific model (or the best) on train+validation data,
    then evaluate on the held-out test set for final reporting.

    This is useful after model selection — you pick the best model,
    then retrain it using all available non-test data for maximum
    performance.

    Args:
        dataset_path: Path to the CSV dataset.
        model_name: Name of the model to retrain. If None, uses the best model.

    Returns:
        Dictionary with the retrained model and test metrics.
    """
    df = load_dataset(dataset_path)
    X_train, X_val, X_test, y_train, y_val, y_test, _scaler, _le = \
        preprocess_and_split(df, save_scaler=True)

    # Combine train + validation
    X_full_train = np.vstack([X_train, X_val])
    y_full_train = np.concatenate([y_train, y_val])

    models = get_models()
    if model_name is None:
        meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
        if os.path.exists(meta_path):
            meta = joblib.load(meta_path)
            model_name = meta["name"]
        else:
            model_name = "Random Forest"

    model = models[model_name]
    model.fit(X_full_train, y_full_train)

    test_metrics = evaluate_model(model, X_test, y_test, LABEL_CLASSES)

    # Save
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, "best_model.joblib"))
    joblib.dump({"name": model_name, "metrics": test_metrics},
                os.path.join(MODELS_DIR, "best_model_meta.joblib"))

    return {
        "model_name": model_name,
        "model": model,
        "test_metrics": test_metrics,
    }


# Allow running as a script
if __name__ == "__main__":
    results = train_all_models(verbose=True)
