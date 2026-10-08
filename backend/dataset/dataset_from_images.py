"""
Dataset from Images — Visionlytics.

Generates dataset rows from a folder of images by running person detection
and feature extraction on each image. This allows users to augment the
synthetic dataset with real-world data.

V2 Improvements:
    - Multi-feature scoring for auto-labeling (not just people_count)
    - Weighted combination of count, occupancy, and inter-person distance
    - Support for batch processing with progress reporting
    - Deduplication when appending to existing datasets

Usage:
    python dataset/dataset_from_images.py --input_dir path/to/images --output dataset/crowd_dataset.csv
"""

import argparse
import os
import sys

import cv2
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from computer_vision.feature_extraction import FeatureExtractor
from computer_vision.person_detection import PersonDetector


def auto_label(features: dict) -> str:
    """
    Automatically assign a density label using multi-feature scoring.

    Uses a weighted combination of people count, occupancy ratio, and
    inter-person distance to produce a continuous density score, then
    maps it to LOW / MEDIUM / HIGH.

    This is more accurate than simple count thresholds because it accounts
    for camera perspective (distant people have smaller boxes but higher
    physical density) and spatial distribution.

    Args:
        features: Dictionary of extracted spatial features.

    Returns:
        Density label string: "LOW", "MEDIUM", or "HIGH".
    """
    people_count = float(features.get("people_count", 0))
    occupancy = float(features.get("occupancy_ratio", 0.0))
    avg_dist = float(features.get("avg_distance", 1.0))
    min_dist = float(features.get("min_distance", 1.0))
    spatial_spread = float(features.get("spatial_spread", 0.0))

    if people_count == 0:
        return "LOW"

    # ── Multi-feature density score ──────────────────────────────────────
    # Each component is normalized to roughly [0, 1] and weighted.
    #
    # count_signal:    More people → higher density
    # occupancy_signal: Higher frame coverage → higher density
    # proximity_signal: Lower avg distance → higher density (inverted)
    # packing_signal:   Lower min distance → more tightly packed (inverted)

    count_signal = min(people_count / 25.0, 1.0)          # saturates at 25
    occupancy_signal = min(occupancy / 0.5, 1.0)          # saturates at 50%
    proximity_signal = max(0.0, 1.0 - avg_dist / 0.6)    # inverted, saturates at dist=0
    packing_signal = max(0.0, 1.0 - min_dist / 0.3)      # inverted
    spread_signal = min(spatial_spread / 0.4, 1.0)        # moderate spread = mid density

    # Weighted combination (sums to 1.0)
    composite = (
        0.30 * count_signal +
        0.25 * occupancy_signal +
        0.20 * proximity_signal +
        0.15 * packing_signal +
        0.10 * spread_signal
    )

    # ── Hard overrides for extreme cases ─────────────────────────────────
    if people_count >= 20 or occupancy > 0.5:
        return "HIGH"
    if people_count <= 2 and occupancy < 0.05 and avg_dist > 0.5:
        return "LOW"

    # ── Threshold-based classification ───────────────────────────────────
    if composite >= 0.50:
        return "HIGH"
    elif composite >= 0.22:
        return "MEDIUM"
    else:
        return "LOW"


def process_images(
    input_dir: str,
    output_path: str | None = None,
    append: bool = True,
    confidence: float = 0.3,
    deduplicate: bool = True,
) -> pd.DataFrame:
    """
    Process all images in a directory and generate dataset rows.

    Args:
        input_dir: Directory containing images (JPG, JPEG, PNG).
        output_path: Path for the output CSV. Defaults to dataset/crowd_dataset.csv.
        append: If True, append to existing CSV. If False, overwrite.
        confidence: Detection confidence threshold.
        deduplicate: If True, skip images already in the dataset (by filename).

    Returns:
        DataFrame with generated rows.
    """
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "crowd_dataset.csv")

    # Initialize detector and extractor
    detector = PersonDetector(confidence_threshold=confidence)
    extractor = FeatureExtractor()

    # Find all images
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    image_files = []
    for f in sorted(os.listdir(input_dir)):
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            image_files.append(os.path.join(input_dir, f))

    if not image_files:
        print(f"No images found in '{input_dir}'")
        return pd.DataFrame()

    # Check for existing entries to skip duplicates
    existing_files = set()
    if deduplicate and append and os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        if "source_file" in existing_df.columns:
            existing_files = set(existing_df["source_file"].dropna().values)

    print(f"Processing {len(image_files)} images...")
    if existing_files:
        print(f"  ({len(existing_files)} already in dataset — will skip duplicates)")

    rows = []
    skipped = 0
    for i, img_path in enumerate(image_files):
        basename = os.path.basename(img_path)

        if basename in existing_files:
            skipped += 1
            continue

        print(f"  [{i+1}/{len(image_files)}] {basename}...", end=" ")

        try:
            image = cv2.imread(img_path)
            if image is None:
                print("SKIP (cannot read)")
                continue

            h, w = image.shape[:2]

            # Detect people
            detections = detector.detect(image)

            # Extract features
            features = extractor.extract(detections, (h, w))

            # Auto-label using multi-feature scoring
            features["density_label"] = auto_label(features)
            features["source_file"] = basename

            rows.append(features)
            print(f"→ {int(features['people_count'])} people, {features['density_label']}")

        except Exception as e:
            print(f"ERROR ({e})")
            continue

    new_df = pd.DataFrame(rows)

    if len(new_df) == 0:
        print(f"No new images processed. ({skipped} skipped as duplicates)")
        return new_df

    # Save or append
    if append and os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        # Drop source_file column from new data if existing doesn't have it
        if "source_file" in new_df.columns and "source_file" not in existing_df.columns:
            new_df = new_df.drop(columns=["source_file"])
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(output_path, index=False)
        print(f"\nAppended {len(new_df)} rows to {output_path} (total: {len(combined_df)})")
        if skipped:
            print(f"  ({skipped} duplicates skipped)")
    else:
        if "source_file" in new_df.columns:
            new_df = new_df.drop(columns=["source_file"])
        new_df.to_csv(output_path, index=False)
        print(f"\nSaved {len(new_df)} rows to {output_path}")

    return new_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate crowd density dataset from images"
    )
    parser.add_argument(
        "--input_dir", "-i", required=True,
        help="Directory containing images"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output CSV path (default: dataset/crowd_dataset.csv)"
    )
    parser.add_argument(
        "--append", action="store_true", default=True,
        help="Append to existing CSV"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing CSV"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.3,
        help="Detection confidence threshold"
    )
    parser.add_argument(
        "--no-dedup", action="store_true",
        help="Disable duplicate skipping"
    )

    args = parser.parse_args()
    process_images(
        input_dir=args.input_dir,
        output_path=args.output,
        append=not args.overwrite,
        confidence=args.confidence,
        deduplicate=not args.no_dedup,
    )
