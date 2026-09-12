# VISIONLYTICS

**Intelligent Visual Crowd Analytics** — a Streamlit computer-vision and statistical machine-learning platform for estimating crowd density from images, video, and camera input.

[![Streamlit](https://img.shields.io/badge/Streamlit-1.63-red?style=flat-square)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8s-Computer%20Vision-green?style=flat-square)](https://docs.ultralytics.com/)

## Overview

VISIONLYTICS combines **YOLOv8s person detection**, spatial feature engineering, and classical statistical machine learning to classify crowd density into **LOW**, **MEDIUM**, and **HIGH** regimes.

The application supports:

- Image analysis with bounding boxes and heatmaps
- Video analysis with person tracking and density trends
- Browser camera snapshots for hosted deployments
- A local live-camera mode for compatible desktop environments
- Ten spatial features for interpretable statistical modelling
- Model benchmarking across Logistic Regression, KNN, Decision Tree, Random Forest, SVM, Gradient Boosting, and a Voting Ensemble
- Dataset inspection, correlation analysis, and model evaluation

## Architecture

```text
Image / Video / Camera
        │
        ▼
   YOLOv8s detector
        │
        ▼
 Person detections
        │
        ├──────────────► Heatmap / Tracking / Visual analytics
        │
        ▼
  Spatial features (10)
        │
        ▼
 Feature scaling
        │
        ▼
 Statistical ML models
        │
        ▼
 LOW / MEDIUM / HIGH
        │
        ▼
 Streamlit dashboard
```

## Repository layout

```text
Visionlytics/
├── app/
│   ├── components/          # UI styling, charts, icons, metrics
│   ├── ui/                  # Dashboard pages
│   ├── database.py          # SQLite history storage
│   ├── main.py              # Streamlit entrypoint
│   └── resources.py         # Cached model/resource loaders
├── computer_vision/         # Detection, tracking, feature extraction, heatmaps
├── dataset/                 # Dataset generation and loading utilities
├── machine_learning/        # Preprocessing, training, evaluation, prediction
├── models/                  # Trained model artifacts used at runtime
├── tests/                   # Automated tests
├── .github/workflows/       # Continuous integration
├── .streamlit/config.toml   # Streamlit UI configuration
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## Installation

```bash
git clone https://github.com/ivin-baiju/Visionlytics.git
cd Visionlytics

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run locally

Start the Streamlit application from the repository root:

```bash
streamlit run app/main.py
```

Then open the local URL shown by Streamlit.

## Machine-learning workflow

The repository includes utilities for creating the synthetic benchmark dataset and training the statistical models.

```bash
python3 -c "from dataset.generate_dataset import generate_dataset; generate_dataset()"
python3 machine_learning/train.py
```

The prediction layer loads the persisted champion model and scaler from `models/`.

## Features

### Image Analysis
Upload a still image, detect people, inspect the ten spatial features, view the density prediction, and compare class probabilities.

### Video Analysis
Process recorded video, track people across frames, and visualize density changes over time.

### Live Camera
Hosted deployments should use the browser snapshot control. Direct `cv2.VideoCapture()` access is intended for local environments where the process can access a camera device.

### ML Models
Train and compare the supported classifiers, inspect confusion matrices and feature importance, and select the best-performing model.

### Dataset
Inspect the feature dataset, distributions, and relationships between variables.

## Spatial feature vector

The model uses these ten features:

1. `people_count`
2. `occupancy_ratio`
3. `avg_person_area`
4. `avg_distance`
5. `min_distance`
6. `spatial_spread`
7. `top_region_count`
8. `middle_region_count`
9. `bottom_region_count`
10. `frame_occupancy_density`

Distances and spatial quantities are normalized so the same feature representation can be used across different image resolutions.

## Model training and evaluation

The training pipeline supports:

- Multinomial Logistic Regression
- K-Nearest Neighbors
- Decision Tree
- Random Forest
- Support Vector Machine (RBF)
- Gradient Boosting
- Soft Voting Ensemble

The repository uses separate training, validation, and held-out test partitions, with feature scaling fitted only on the training partition.

## Configuration

Streamlit configuration lives in `.streamlit/config.toml`.

Runtime-generated files such as SQLite history and logs are written under `outputs/` and are intentionally excluded from version control.

## Development

Run the tracked test suite with:

```bash
python tests/test_tracking.py
```

GitHub Actions runs the same test command on Python 3.11 for every push and pull request to `main`.

## Notes

- The primary detector is **YOLOv8s** (`yolov8s.onnx`, with `yolov8s.pt` as fallback).
- Large generated artifacts should not be committed unless they are required for the application to run.
- Training artifacts are ignored by default so new local retraining runs do not pollute the repository.

## Project status

VISIONLYTICS is an academic/engineering project focused on interpretable crowd-density analytics using computer vision and statistical machine learning.
