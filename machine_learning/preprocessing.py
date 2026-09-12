"""
Data Preprocessing Module for Visionlytics.

Handles loading the crowd density dataset, cleaning, scaling, encoding,
and splitting into train/validation/test sets.

Key ML Concepts Demonstrated:
    - Feature Scaling: StandardScaler normalizes features to zero mean and
      unit variance, which is important for distance-based algorithms (KNN, SVM).
    - Label Encoding: Converts string labels (LOW, MEDIUM, HIGH) to integers.
    - Train/Test Split: Stratified splitting ensures each class is proportionally
      represented in all sets. We use 70/15/15 split.
    - Data Leakage Prevention: The scaler is fit ONLY on training data.
"""

import os
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib


# ── Constants ─────────────────────────────────────────────────────────────────

FEATURE_COLUMNS = [
    "people_count",
    "occupancy_ratio",
    "avg_person_area",
    "avg_distance",
    "min_distance",
    "spatial_spread",
    "top_region_count",
    "middle_region_count",
    "bottom_region_count",
    "frame_occupancy_density",
]

LABEL_COLUMN = "density_label"

LABEL_CLASSES = ["LOW", "MEDIUM", "HIGH"]

# Default paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "crowd_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")


def load_dataset(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load the crowd density dataset from CSV.

    Args:
        path: Path to the CSV file. Defaults to dataset/crowd_dataset.csv.

    Returns:
        Pandas DataFrame with features and labels.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        ValueError: If required columns are missing.
    """
    csv_path = path or DATASET_PATH

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at '{csv_path}'. "
            "Run dataset/generate_dataset.py to create it."
        )

    df = pd.read_csv(csv_path)

    # Validate required columns
    required = FEATURE_COLUMNS + [LABEL_COLUMN]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    return df


def check_data_quality(df: pd.DataFrame) -> Dict:
    """
    Check data quality and report issues.

    Returns:
        Dictionary with data quality statistics.
    """
    quality = {
        "total_rows": len(df),
        "missing_values": df[FEATURE_COLUMNS].isnull().sum().to_dict(),
        "total_missing": int(df[FEATURE_COLUMNS].isnull().sum().sum()),
        "class_distribution": df[LABEL_COLUMN].value_counts().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "feature_stats": df[FEATURE_COLUMNS].describe().to_dict(),
    }
    return quality


def preprocess_and_split(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
    save_scaler: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, LabelEncoder]:
    """
    Preprocess the dataset and split into train/validation/test sets.

    Steps:
        1. Handle missing values (fill with column median)
        2. Encode labels: LOW=0, MEDIUM=1, HIGH=2
        3. Split into train (70%), validation (15%), test (15%) — stratified
        4. Scale features using StandardScaler (fit on train only)

    IMPORTANT: The scaler is fit ONLY on the training data to prevent
    data leakage. Validation and test data are transformed using the
    same scaler without refitting.

    Args:
        df: Input DataFrame with features and labels.
        test_size: Fraction of data for the test set.
        val_size: Fraction of data for the validation set.
        random_state: Random seed for reproducibility.
        save_scaler: Whether to save the scaler to disk.

    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder)
    """
    # ── Step 0: Extract Features and Labels ──────────────────────────────
    X = df[FEATURE_COLUMNS].copy()
    y = df[LABEL_COLUMN].copy()

    # ── Step 1: Label encoding ───────────────────────────────────────────
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(LABEL_CLASSES)
    y_encoded = label_encoder.transform(y)

    # ── Step 2: Stratified train/val/test split ──────────────────────────
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y_encoded,
        test_size=test_size,
        random_state=random_state,
        stratify=y_encoded,
    )

    # Second split: separate validation from training
    # Adjust val_size relative to the remaining data
    relative_val_size = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=relative_val_size,
        random_state=random_state,
        stratify=y_temp,
    )

    # ── Step 3: Handle missing values without data leakage ───────────────
    # Compute medians on training set ONLY
    train_medians = X_train.median()
    
    # Apply to all sets
    for col in FEATURE_COLUMNS:
        X_train[col] = X_train[col].fillna(train_medians[col])
        X_val[col] = X_val[col].fillna(train_medians[col])
        X_test[col] = X_test[col].fillna(train_medians[col])

    # Convert to numpy arrays for scaling
    X_train_np = X_train.values
    X_val_np = X_val.values
    X_test_np = X_test.values

    # ── Step 4: Feature scaling (fit on TRAINING data only) ──────────────
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_np)  # Fit + transform on train
    X_val = scaler.transform(X_val_np)           # Transform only on validation
    X_test = scaler.transform(X_test_np)         # Transform only on test

    # Save the scaler for use during prediction
    if save_scaler:
        os.makedirs(MODELS_DIR, exist_ok=True)
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        joblib.dump(scaler, scaler_path)
        le_path = os.path.join(MODELS_DIR, "label_encoder.joblib")
        joblib.dump(label_encoder, le_path)

    return X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder


def scale_features(features: Dict[str, float], scaler: Optional[StandardScaler] = None) -> np.ndarray:
    """
    Scale a single feature vector for prediction.

    Args:
        features: Dictionary of feature name → value.
        scaler: Fitted StandardScaler. If None, loads from disk.

    Returns:
        Scaled feature array of shape (1, n_features).
    """
    if scaler is None:
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError("Scaler not found. Train the models first.")
        scaler = joblib.load(scaler_path)

    # Build feature vector in the correct column order
    feature_vector = np.array([[features.get(col, 0.0) for col in FEATURE_COLUMNS]])

    return scaler.transform(feature_vector)
