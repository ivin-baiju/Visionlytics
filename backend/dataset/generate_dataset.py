"""
Synthetic Dataset Generator for Visionlytics.

Generates a synthetic crowd density dataset with realistic feature vectors
for training the ML classifiers. Each row represents the features that
would be extracted from one image analysis.

The dataset has three classes:
    LOW    — Sparse crowd (0-4 people)
    MEDIUM — Moderate crowd (3-12 people)
    HIGH   — Dense crowd (10+ people)

V2 Improvements:
    - 5,000 samples by default (up from 1,500) for better generalization
    - Overlapping class boundaries at 3-4 and 10-12 people for realism
    - Camera perspective simulation (bird's-eye, eye-level, elevated)
    - Edge cases: 0 people, 1 person, 100+ extreme density
    - Correlated feature noise (inter-feature dependencies preserved)

This synthetic approach allows the ML pipeline to work immediately
without requiring a pre-labeled image dataset. Users can supplement
this with real data using the dataset_from_images.py tool.
"""

import os

import numpy as np
import pandas as pd

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

# Camera perspective profiles — each simulates a different mounting angle
# and affects how spatial features relate to each other.
PERSPECTIVE_PROFILES = {
    "eye_level": {
        "depth_weight_range": (1.0, 4.0),   # strong perspective compression
        "area_scale": 1.0,
        "distance_scale": 1.0,
    },
    "elevated": {
        "depth_weight_range": (1.0, 2.5),   # moderate perspective
        "area_scale": 0.8,
        "distance_scale": 1.1,
    },
    "birds_eye": {
        "depth_weight_range": (1.0, 1.3),   # nearly uniform — top-down view
        "area_scale": 0.6,
        "distance_scale": 1.3,
    },
}


def generate_dataset(
    n_per_class: int = 1667,
    output_path: str | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic crowd density dataset.

    Creates n_per_class samples for each of LOW, MEDIUM, HIGH
    (default: 1667 × 3 ≈ 5,000 total samples).

    Features are drawn from class-appropriate distributions with noise,
    camera perspective variation, and realistic edge cases.

    Args:
        n_per_class: Number of samples to generate per class.
        output_path: Where to save the CSV. Defaults to dataset/crowd_dataset.csv.
        random_state: Random seed for reproducibility.

    Returns:
        Generated DataFrame.
    """
    np.random.seed(random_state)

    all_rows = []

    # ── LOW Density (0–4 people) ─────────────────────────────────────────
    for _ in range(n_per_class):
        perspective = _random_perspective()
        row = _generate_low_density(perspective)
        row["density_label"] = "LOW"
        all_rows.append(row)

    # ── MEDIUM Density (3–12 people) ─────────────────────────────────────
    for _ in range(n_per_class):
        perspective = _random_perspective()
        row = _generate_medium_density(perspective)
        row["density_label"] = "MEDIUM"
        all_rows.append(row)

    # ── HIGH Density (10+ people) ────────────────────────────────────────
    for _ in range(n_per_class):
        perspective = _random_perspective()
        row = _generate_high_density(perspective)
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

    total = len(df)
    print(f"Generated {total} samples → {output_path}")
    print(f"  LOW: {n_per_class}, MEDIUM: {n_per_class}, HIGH: {n_per_class}")

    return df


def _random_perspective() -> dict:
    """Select a random camera perspective profile."""
    name = np.random.choice(list(PERSPECTIVE_PROFILES.keys()), p=[0.5, 0.3, 0.2])
    return PERSPECTIVE_PROFILES[name]


def _generate_low_density(perspective: dict) -> dict:
    """Generate feature vector for LOW crowd density (0–4 people with overlap zone)."""
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

    area_scale = perspective["area_scale"]
    dist_scale = perspective["distance_scale"]

    occupancy_ratio = np.clip(np.random.beta(1.5, 15) * 0.3 * area_scale + _noise(0.01), 0.001, 0.2)
    avg_person_area = occupancy_ratio / max(people_count, 1) + _noise(0.01)
    avg_person_area = np.clip(avg_person_area, 0.001, 0.15)

    avg_distance = np.clip(np.random.uniform(0.35, 0.95) * dist_scale + _noise(0.1), 0.1, 1.0)
    min_distance = np.clip(avg_distance - np.random.uniform(0.05, 0.25), 0.05, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.05, 0.5) + _noise(0.05), 0.0, 0.6)

    regions = _distribute_to_regions(people_count, perspective)

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


def _generate_medium_density(perspective: dict) -> dict:
    """Generate feature vector for MEDIUM crowd density (3–12 people with overlap zones)."""
    people_count = np.random.randint(3, 13)

    area_scale = perspective["area_scale"]
    dist_scale = perspective["distance_scale"]

    occupancy_ratio = np.clip(np.random.beta(3, 5) * 0.6 * area_scale + _noise(0.05), 0.08, 0.6)
    avg_person_area = occupancy_ratio / people_count + _noise(0.005)
    avg_person_area = np.clip(avg_person_area, 0.005, 0.1)

    avg_distance = np.clip(np.random.uniform(0.1, 0.55) * dist_scale + _noise(0.08), 0.05, 0.7)
    min_distance = np.clip(avg_distance - np.random.uniform(0.05, 0.2), 0.02, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.1, 0.45) + _noise(0.05), 0.05, 0.6)

    regions = _distribute_to_regions(people_count, perspective)

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


def _generate_high_density(perspective: dict) -> dict:
    """Generate feature vector for HIGH crowd density (10+ people, including extreme)."""
    # Occasionally generate extreme-density edge cases (100+)
    if np.random.random() < 0.08:
        people_count = np.random.randint(60, 150)
    else:
        people_count = np.random.randint(10, 60)

    area_scale = perspective["area_scale"]
    dist_scale = perspective["distance_scale"]

    occupancy_ratio = np.clip(
        np.random.beta(5, 3) * 0.8 * area_scale + 0.15 + _noise(0.05), 0.25, 0.98
    )
    avg_person_area = occupancy_ratio / people_count + _noise(0.003)
    avg_person_area = np.clip(avg_person_area, 0.002, 0.08)

    avg_distance = np.clip(np.random.uniform(0.01, 0.25) * dist_scale + _noise(0.03), 0.005, 0.35)
    min_distance = np.clip(avg_distance - np.random.uniform(0.005, 0.1), 0.002, avg_distance)

    spatial_spread = np.clip(np.random.uniform(0.05, 0.4) + _noise(0.05), 0.02, 0.5)

    regions = _distribute_to_regions(people_count, perspective)

    frame_occupancy_density = np.clip(
        people_count * np.random.uniform(1.5, 4.0) + _noise(0.5), 10.0, 400.0
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


def _distribute_to_regions(total: int, perspective: dict | None = None) -> tuple:
    """
    Randomly distribute people across top/middle/bottom regions.

    The distribution is influenced by camera perspective:
        - Eye-level: more people in the middle/bottom
        - Bird's-eye: roughly uniform
        - Elevated: slight middle bias

    Args:
        total: Total number of people to distribute.
        perspective: Camera perspective profile (optional).

    Returns:
        Tuple of (top_count, middle_count, bottom_count).
    """
    if total == 0:
        return (0, 0, 0)

    if perspective is not None:
        depth_lo, depth_hi = perspective["depth_weight_range"]
        # Stronger perspective → more people in bottom/middle
        if depth_hi > 3.0:
            # Eye-level: bottom-heavy
            probs = np.random.dirichlet([0.8, 1.5, 1.7])
        elif depth_hi > 2.0:
            # Elevated
            probs = np.random.dirichlet([1.0, 1.5, 1.0])
        else:
            # Bird's eye: roughly uniform
            probs = np.random.dirichlet([1.2, 1.2, 1.2])
    else:
        probs = np.random.dirichlet([1.0, 1.5, 1.0])

    counts = np.random.multinomial(total, probs)
    return (int(counts[0]), int(counts[1]), int(counts[2]))


def _noise(scale: float) -> float:
    """Generate Gaussian noise with the given scale."""
    return np.random.normal(0, scale)


# Allow running as a script
if __name__ == "__main__":
    generate_dataset()
