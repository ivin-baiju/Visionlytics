"""
Dataset & ML Model REST endpoints for Visionlytics.

Exposes the dataset and the trained statistical-ML model registry over HTTP so
the Streamlit frontend no longer needs to import `machine_learning.*` or
`dataset.*` directly. All payloads are plain JSON-serializable types.
"""

import os

import joblib
import numpy as np
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from dataset.generate_dataset import generate_dataset
from machine_learning.preprocessing import (
    DATASET_PATH,
    FEATURE_COLUMNS,
    LABEL_CLASSES,
    MODELS_DIR,
    load_dataset,
)
from machine_learning.train import train_all_models

router = APIRouter(tags=["dataset", "models"])

# Cap on rows shipped to the browser for previews/charts.
MAX_PREVIEW_ROWS = 3000


def _dataset_payload(df, limit: int = MAX_PREVIEW_ROWS) -> dict:
    """Serialize a dataset DataFrame into a JSON-safe preview payload."""
    subset = df.head(limit)
    return {
        "columns": list(subset.columns),
        "rows": subset.values.tolist(),
        "n_rows": int(len(df)),
        "n_preview_rows": int(len(subset)),
        "feature_columns": FEATURE_COLUMNS,
        "class_labels": LABEL_CLASSES,
        "class_counts": {str(k): int(v) for k, v in df["density_label"].value_counts().items()},
        "missing_values": int(df.isnull().sum().sum()),
        "source": "api",
    }


# ── Dataset endpoints ────────────────────────────────────────────────────────

@router.get("/dataset/preview")
def dataset_preview(limit: int = MAX_PREVIEW_ROWS):
    """Return dataset rows (capped) plus summary counts for the UI."""
    try:
        df = load_dataset(DATASET_PATH)
    except (FileNotFoundError, ValueError) as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(status_code=500, content={"error": f"Failed to load dataset: {exc}"})

    return _dataset_payload(df, limit=limit)


@router.get("/dataset/info")
def dataset_info():
    """Return lightweight dataset metadata without shipping any rows."""
    try:
        df = load_dataset(DATASET_PATH)
    except (FileNotFoundError, ValueError) as exc:
        return JSONResponse(
            status_code=404,
            content={"error": str(exc), "dataset_path": DATASET_PATH, "exists": False},
        )
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(status_code=500, content={"error": f"Failed to load dataset: {exc}"})

    return {
        "dataset_path": DATASET_PATH,
        "exists": True,
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "feature_columns": FEATURE_COLUMNS,
        "class_labels": LABEL_CLASSES,
        "class_counts": {str(k): int(v) for k, v in df["density_label"].value_counts().items()},
        "missing_values": int(df.isnull().sum().sum()),
    }


@router.post("/dataset/generate")
def dataset_generate(n_per_class: int = 500):
    """Regenerate the synthetic dataset and return a fresh preview payload."""
    if n_per_class < 100 or n_per_class > 50000:
        return JSONResponse(
            status_code=400,
            content={"error": "n_per_class must be between 100 and 50000"},
        )

    try:
        df = generate_dataset(n_per_class=n_per_class, output_path=DATASET_PATH)
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(status_code=500, content={"error": f"Generation failed: {exc}"})

    payload = _dataset_payload(df)
    payload["generated"] = True
    payload["n_per_class"] = int(n_per_class)
    return payload


# ── Model registry endpoints ─────────────────────────────────────────────────

@router.get("/models/list")
def models_list():
    """Return which trained model artifacts exist on disk plus the champion."""
    expected = {
        "Logistic Regression": "logistic_regression.joblib",
        "KNN": "knn.joblib",
        "Decision Tree": "decision_tree.joblib",
        "Random Forest": "random_forest.joblib",
        "SVM": "svm.joblib",
        "Gradient Boosting": "gradient_boosting.joblib",
        "Voting Ensemble": "voting_ensemble.joblib",
    }

    artifacts = {}
    for name, fname in expected.items():
        path = os.path.join(MODELS_DIR, fname)
        present = os.path.exists(path)
        artifacts[name] = {
            "file": fname,
            "present": present,
            "size_bytes": os.path.getsize(path) if present else 0,
        }

    best_model_name = None
    meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
    if os.path.exists(meta_path):
        try:
            best_model_name = joblib.load(meta_path).get("name")
        except Exception:  # pragma: no cover - defensive
            best_model_name = None

    return {
        "models_dir": MODELS_DIR,
        "has_trained_models": os.path.exists(os.path.join(MODELS_DIR, "best_model.joblib")),
        "has_evaluation_results": os.path.exists(
            os.path.join(MODELS_DIR, "evaluation_results.joblib")
        ),
        "best_model_name": best_model_name,
        "artifacts": artifacts,
        "class_labels": LABEL_CLASSES,
        "feature_columns": FEATURE_COLUMNS,
    }


@router.get("/models/evaluation")
def models_evaluation():
    """Return the saved validation/test metrics for all trained models."""
    results_path = os.path.join(MODELS_DIR, "evaluation_results.joblib")
    if not os.path.exists(results_path):
        return JSONResponse(
            status_code=404,
            content={"error": "No saved evaluation results. Train the models first."},
        )

    try:
        results = joblib.load(results_path)
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(status_code=500, content={"error": f"Failed to load results: {exc}"})

    return {
        "val_metrics": results.get("val_metrics", {}),
        "test_metrics": results.get("test_metrics", {}),
        "training_times": results.get("training_times", {}),
        "best_model_name": results.get("best_model_name"),
        "data_info": results.get("data_info", {}),
        "class_labels": LABEL_CLASSES,
        "feature_columns": FEATURE_COLUMNS,
    }


@router.get("/models/feature-importance")
def models_feature_importance(model_name: str | None = None):
    """Return feature importances for the champion (or a named) model."""
    resolved_name = model_name

    if resolved_name is None:
        meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
        if os.path.exists(meta_path):
            try:
                resolved_name = joblib.load(meta_path).get("name")
            except Exception:  # pragma: no cover - defensive
                resolved_name = None

    # Prefer Random Forest (always has native importances), then the champion.
    candidates = [c for c in ("Random Forest", resolved_name) if c]
    for name in candidates:
        safe = name.lower().replace(" ", "_")
        path = os.path.join(MODELS_DIR, f"{safe}.joblib")
        if not os.path.exists(path):
            continue

        try:
            model = joblib.load(path)
        except Exception:  # pragma: no cover - defensive
            continue

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_.tolist()
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_).mean(axis=0).tolist()
        else:
            continue

        return {
            "model_name": name,
            "feature_names": FEATURE_COLUMNS,
            "importances": [float(v) for v in importances],
        }

    return JSONResponse(
        status_code=404,
        content={"error": "Feature importance unavailable for the available models."},
    )


@router.post("/models/train")
def models_train():
    """Retrain all 7 models and return metrics plus the refreshed registry."""
    try:
        results = train_all_models(verbose=False)
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(status_code=500, content={"error": f"Training failed: {exc}"})

    return {
        "val_metrics": results["val_metrics"],
        "test_metrics": results["test_metrics"],
        "training_times": results["training_times"],
        "best_model_name": results["best_model_name"],
        "data_info": results["data_info"],
        "class_labels": LABEL_CLASSES,
        "feature_columns": FEATURE_COLUMNS,
        "trained": True,
    }
