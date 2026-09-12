# VISIONLYTICS

**Intelligent Visual Crowd Analytics** — a Streamlit computer-vision and statistical machine-learning platform for estimating crowd density from images, video, and camera input.

[![Version](https://img.shields.io/badge/Version-1.0-636ee6?style=flat-square)](VERSION_1.0.md)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63-red?style=flat-square)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8s-Computer%20Vision-green?style=flat-square)](https://docs.ultralytics.com/)

## Overview

VISIONLYTICS combines **YOLOv8s person detection**, spatial feature engineering, and classical statistical machine learning to classify crowd density into **LOW**, **MEDIUM**, and **HIGH** regimes.

The application supports image analysis, video analysis with tracking, browser camera snapshots, local camera input, interpretable spatial features, model benchmarking, dataset inspection, and statistical evaluation.

## Architecture

```text
Image / Video / Camera
        │
        ▼
   YOLOv8s detector
        │
        ▼
 Person detections ─────► Heatmap / Tracking / Visual analytics
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
├── models/                  # Runtime model artifacts
├── tests/                   # Tests
├── .github/workflows/       # Continuous integration
├── .streamlit/config.toml   # Streamlit configuration
├── requirements.txt         # Python dependencies
├── .gitignore
├── README.md
└── VERSION_1.0.md
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

```bash
streamlit run app/main.py
```

## Machine-learning workflow

Generate the benchmark dataset and train the supported classifiers:

```bash
python3 -c "from dataset.generate_dataset import generate_dataset; generate_dataset()"
python3 machine_learning/train.py
```

The prediction layer loads the persisted model and scaler from `models/`.

## Application pages

### Image Analysis
Upload an image, detect people, inspect the ten spatial features, view the density prediction, and compare class probabilities.

### Video Analysis
Process recorded video, track people across frames, and visualize density changes over time.

### Live Camera
Hosted deployments should use the browser camera snapshot control. Direct `cv2.VideoCapture()` access is intended for compatible local environments.

### ML Models
Train and compare the supported classifiers, inspect evaluation metrics, confusion matrices, and feature importance.

### Dataset
Inspect the feature dataset, distributions, and relationships between variables.

## Spatial features

The model uses:

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

## Models

- Multinomial Logistic Regression
- K-Nearest Neighbors
- Decision Tree
- Random Forest
- Support Vector Machine (RBF)
- Gradient Boosting
- Soft Voting Ensemble

The training pipeline keeps training, validation, and held-out test data separate and fits feature scaling only on the training partition.

## Configuration

Streamlit configuration lives in `.streamlit/config.toml`.

Runtime-generated files such as SQLite history and logs are written to `outputs/`, which is excluded from version control.

## Testing

Run the tracking tests directly:

```bash
python tests/test_tracking.py
```

GitHub Actions runs the lightweight tracking test on Python 3.11 for pushes and pull requests to `main`.

## Deployment

For Streamlit hosting, use the repository root with `app/main.py` as the application entrypoint.

The repository intentionally excludes Snowflake and Docker deployment configuration from the supported 1.0 runtime path.

## Version 1.0

Version 1.0 is the cleaned Streamlit-focused release with repository simplification, detector hardening, improved runtime checks, and a lightweight CI pipeline. See [`VERSION_1.0.md`](VERSION_1.0.md) for the release notes.

## Project status

VISIONLYTICS is an academic/engineering project focused on interpretable crowd-density analytics using computer vision and statistical machine learning.
