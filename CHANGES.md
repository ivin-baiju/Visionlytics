# Visionlytics — Changelog & Master Project State

This file consolidates all modifications, efficiency improvements, Docker-free execution changes, dataset expansion, training data, and UI updates applied to the project.

---

## 1. Local Execution & Docker Removal
- **Single-Process Launcher (`start_local.py`)**:
  - Eliminates the need for Docker Desktop or container runtimes on macOS.
  - Automatically targets the project virtual environment (`.venv/bin/python`).
  - Launches both the FastAPI backend (`http://127.0.0.1:8000`) and the Streamlit frontend (`http://127.0.0.1:8501`) concurrently.
  - Monitors the `/health` endpoint before opening the user interface.
  - Manages clean, synchronized shutdown of child processes on `Ctrl+C`.
  - Removed obsolete container files (`docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, and legacy bash scripts).
  - **Command**:
    ```bash
    python start_local.py
    ```

---

## 2. Speed & Efficiency Optimizations
- **ONNX-First Inference Engine (`backend/computer_vision/person_detection.py`)**:
  - Configured ONNX Runtime as the primary YOLOv8 inference path using `yolov8s.onnx` (2–4x faster than PyTorch on CPU).
  - Cached device resolution (`_resolve_device`) to prevent per-frame PyTorch imports and avoid macOS Apple Silicon threading locks.
  - Added batch numpy parsing for detection bounding boxes (`_parse_results`).
  - Added `warm_up()` to pre-load model weights and run a dummy frame during FastAPI boot (`backend/main.py`), eliminating initial request latency.
- **Vectorized Feature Extraction (`backend/computer_vision/feature_extraction.py`)**:
  - Replaced pixel-level full-image masks with an analytic sweep-line union area calculator and downsampled masks.
  - Vectorized pairwise Euclidean distances, regional quadrant bins (top, middle, bottom), and spatial spread metrics, eliminating slow Python loops on dense frames.

---

## 3. Dataset & Model Training Enhancements
- **Dataset Expansion (`backend/dataset/generate_dataset.py` & `backend/dataset/crowd_dataset.csv`)**:
  - Scaled dataset from 1,500 samples to **5,001 balanced samples** (`LOW`: 1,667, `MEDIUM`: 1,667, `HIGH`: 1,667).
  - Integrated camera perspective simulation (eye-level, elevated, bird's-eye) and dense crowd scenarios (100+ individuals).
- **Added XGBoost & Enhanced ML Models (`backend/machine_learning/models.py`)**:
  - Integrated `xgboost` into the model suite as an 8th classifier.
  - Increased Random Forest to 200 estimators; tuned SVM with RBF kernel and calibrated probabilities; tuned Gradient Boosting (`subsample=0.8`).
  - Updated Voting Ensemble meta-classifier to include XGBoost.
- **Model Training Pipeline (`backend/machine_learning/train.py`)**:
  - Trained all 8 algorithms with 70/15/15 stratified train/val/test splits and 5-fold cross-validation.
  - Saved updated model weights to the `models/` directory:
    - Logistic Regression (`logistic_regression.joblib`)
    - K-Nearest Neighbors (`knn.joblib`)
    - Decision Tree (`decision_tree.joblib`)
    - Random Forest (`random_forest.joblib`)
    - Support Vector Machine (`svm.joblib`)
    - Gradient Boosting (`gradient_boosting.joblib`)
    - XGBoost (`xgboost.joblib`)
    - Voting Ensemble (`voting_ensemble.joblib`)
    - Scaler & Metadata (`scaler.joblib`, `best_model.joblib`, `best_model_meta.joblib`)
  - **Model Performance**: Decision Tree, XGBoost, and Random Forest achieved **>0.996 F1 score**.
- **Multi-Feature Auto-Labeling (`backend/dataset/dataset_from_images.py`)**:
  - Replaced count-only classification with multi-factor scoring (count, occupancy ratio, proximity index, spatial packing, and spread).

---

## 4. UI Clean-Up & High-Contrast Visual Redesign
- **Removed Distracting Colors & Dark Blurs (`.streamlit/config.toml`, `frontend/app/components/styles.py`, `frontend/app/components/theme.py`)**:
  - Replaced illegible dark neon and glowing colors with a crisp, minimal light theme.
  - Set high-contrast dark slate text (`#0F172A`) on pure white surfaces (`#FFFFFF`) with off-white background (`#F8FAFC`).
  - Added clean, semantic status pill badges for density levels:
    - **LOW**: Soft green background (`#DCFCE7`), dark green text (`#166534`).
    - **MEDIUM**: Soft amber background (`#FEF3C7`), dark amber text (`#92400E`).
    - **HIGH**: Soft red background (`#FEE2E2`), dark red text (`#991B1B`).
  - Polished buttons, inputs, file dropzones, and data tables for maximum legibility.
- **Plotly Visualizations (`frontend/app/components/charts.py`)**:
  - Switched charts to transparent/white canvas with high-contrast text and crisp axes.
- **Navigation (`frontend/app/main.py`)**:
  - Added the **ML Models** page back into the sidebar navigation to easily inspect and benchmark all 8 algorithms.

---

## 5. Directory Cleanup
- Removed legacy agent scripts and markdown files (`.agent/`, `.agents/`, `.gemini/`, `.gsd/`, `adapters/`, `scripts/`, `GSD-STYLE.md`, `PROJECT_RULES.md`, `VERSION`, `VERSION_0.5.md`, `model_capabilities.yaml`, `docker-compose.yml`, `start.sh`).
- Cleaned build artifacts (`*.egg-info`, fallback sqlite databases).
- Workspace is now clean, organized, and focused on core project files.
