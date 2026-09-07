"""
Synthetic Dataset Generator for Visionlytics.

Generates a synthetic crowd density dataset with realistic feature vectors
for training the ML classifiers. Each row represents the features that
would be extracted from one image analysis.

The dataset has three classes:
    LOW    — Sparse crowd (0-3 people)
    MEDIUM — Moderate crowd (4-10 people)
    HIGH   — Dense crowd (11+ people)

Feature values are generated using random distributions calibrated to
match real-world crowd scenarios. Gaussian noise is added for realism.

This synthetic approach allows the ML pipeline to work immediately
without requiring a pre-labeled image dataset. Users can supplement
this with real data using the dataset_from_images.py tool.
"""

import os
import numpy as np
import pandas as pd
from typing import Optional


# Feature column names matching the FeatureExtractor output
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


def generate_dataset(
    n_per_class: int = 500,
    output_path: Optional[str] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic crowd density dataset.

    Creates n_per_class samples for each of LOW, MEDIUM, HIGH.
    Features are drawn from class-appropriate distributions with noise.

    Args:
        n_per_class: Number of samples to generate per class.
        output_path: Where to save the CSV. Defaults to dataset/crowd_dataset.csv.
        random_state: Random seed for reproducibility.

    Returns:
        Generated DataFrame.
    """
    np.random.seed(random_state)

    all_rows = []

    # ── LOW Density (0–3 people) ─────────────────────────────────────────
    for _ in range(n_per_class):
        row = _generate_low_density()
        row["density_label"] = "LOW"
        all_rows.append(row)

    # ── MEDIUM Density (4–10 people) ─────────────────────────────────────
    for _ in range(n_per_class):
        row = _generate_medium_density()
        row["density_label"] = "MEDIUM"
        all_rows.append(row)

    # ── HIGH Density (11+ people) ────────────────────────────────────────
    for _ in range(n_per_class):
        row = _generate_high_density()
        row["density_label"] = "HIGH"
        all_rows.append(row)

    df = pd.DataFrame(all_rows)

    # Shuffle the dataset
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

    # Save to CSV
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "crowd_dataset.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} samples → {output_path}")
    print(f"  LOW: {n_per_class}, MEDIUM: {n_per_class}, HIGH: {n_per_class}")

    return df


def _generate_low_density() -> dict:
    """Generate feature vector for LOW crowd density (0–4 people with overlap)."""
    people_count = np.random.randint(0, 5)

    if people_count == 0:
        return {
            "people_count": 0,
            "occupancy_ratio": 0.0,
            "avg_person_area": 0.0,
            "avg_distance": 1.0,
            "min_distance": 1.0,
            "spatial_spread": 0.0,
            "top_region_count": 0,
            "middle_region_count": 0,
            "bottom_region_count": 0,
            "frame_occupancy_density": 0.0,
        }

    occupancy_ratio = np.clip(np.random.beta(1.5, 15) * 0.3 + _noise(0.01), 0.001, 0.2)
    avg_person_area = occupancy_ratio / max(people_count, 1) + _noise(0.01)
    avg_person_area = np.clip(avg_person_area, 0.001, 0.15)

    avg_distance = np.clip(np.random.uniform(0.35, 0.95) + _noise(0.1), 0.1, 1.0)
    min_distance = np.clip(avg_distance - np.random.uniform(0.05, 0.25), 0.05, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.05, 0.5) + _noise(0.05), 0.0, 0.6)

    # Distribute people across regions
    regions = _distribute_to_regions(people_count)

    frame_occupancy_density = np.clip(
        people_count * np.random.uniform(0.3, 1.5) + _noise(0.1), 0.0, 5.0
    )

    return {
        "people_count": people_count,
        "occupancy_ratio": round(occupancy_ratio, 6),
        "avg_person_area": round(avg_person_area, 6),
        "avg_distance": round(avg_distance, 6),
        "min_distance": round(min_distance, 6),
        "spatial_spread": round(spatial_spread, 6),
        "top_region_count": regions[0],
        "middle_region_count": regions[1],
        "bottom_region_count": regions[2],
        "frame_occupancy_density": round(frame_occupancy_density, 6),
    }


def _generate_medium_density() -> dict:
    """Generate feature vector for MEDIUM crowd density (3–12 people with overlap)."""
    people_count = np.random.randint(3, 13)

    occupancy_ratio = np.clip(np.random.beta(3, 5) * 0.6 + _noise(0.05), 0.08, 0.6)
    avg_person_area = occupancy_ratio / people_count + _noise(0.005)
    avg_person_area = np.clip(avg_person_area, 0.005, 0.1)

    avg_distance = np.clip(np.random.uniform(0.1, 0.55) + _noise(0.08), 0.05, 0.7)
    min_distance = np.clip(avg_distance - np.random.uniform(0.05, 0.2), 0.02, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.1, 0.45) + _noise(0.05), 0.05, 0.6)

    regions = _distribute_to_regions(people_count)

    frame_occupancy_density = np.clip(
        people_count * np.random.uniform(1.0, 3.0) + _noise(0.3), 2.0, 25.0
    )

    return {
        "people_count": people_count,
        "occupancy_ratio": round(occupancy_ratio, 6),
        "avg_person_area": round(avg_person_area, 6),
        "avg_distance": round(avg_distance, 6),
        "min_distance": round(min_distance, 6),
        "spatial_spread": round(spatial_spread, 6),
        "top_region_count": regions[0],
        "middle_region_count": regions[1],
        "bottom_region_count": regions[2],
        "frame_occupancy_density": round(frame_occupancy_density, 6),
    }


def _generate_high_density() -> dict:
    """Generate feature vector for HIGH crowd density (10+ people with overlap)."""
    people_count = np.random.randint(10, 60)

    occupancy_ratio = np.clip(np.random.beta(5, 3) * 0.8 + 0.15 + _noise(0.05), 0.25, 0.98)
    avg_person_area = occupancy_ratio / people_count + _noise(0.003)
    avg_person_area = np.clip(avg_person_area, 0.002, 0.08)

    avg_distance = np.clip(np.random.uniform(0.01, 0.25) + _noise(0.03), 0.005, 0.35)
    min_distance = np.clip(avg_distance - np.random.uniform(0.005, 0.1), 0.002, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.05, 0.4) + _noise(0.05), 0.02, 0.5)

    regions = _distribute_to_regions(people_count)

    frame_occupancy_density = np.clip(
        people_count * np.random.uniform(1.5, 4.0) + _noise(0.5), 10.0, 150.0
    )

    return {
        "people_count": people_count,
        "occupancy_ratio": round(occupancy_ratio, 6),
        "avg_person_area": round(avg_person_area, 6),
        "avg_distance": round(avg_distance, 6),
        "min_distance": round(min_distance, 6),
        "spatial_spread": round(spatial_spread, 6),
        "top_region_count": regions[0],
        "middle_region_count": regions[1],
        "bottom_region_count": regions[2],
        "frame_occupancy_density": round(frame_occupancy_density, 6),
    }


def _distribute_to_regions(total: int) -> tuple:
    """
    Randomly distribute people across top/middle/bottom regions.

    Args:
        total: Total number of people to distribute.

    Returns:
        Tuple of (top_count, middle_count, bottom_count).
    """
    if total == 0:
        return (0, 0, 0)

    # Random multinomial distribution with slight middle bias
    probs = np.random.dirichlet([1.0, 1.5, 1.0])
    counts = np.random.multinomial(total, probs)
    return (int(counts[0]), int(counts[1]), int(counts[2]))


def _noise(scale: float) -> float:
    """Generate Gaussian noise with the given scale."""
    return np.random.normal(0, scale)


# Allow running as a script
if __name__ == "__main__":
    generate_dataset()
