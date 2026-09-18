"""
Dataset from Images — Visionlytics.

Generates dataset rows from a folder of images by running person detection
and feature extraction on each image. This allows users to augment the
synthetic dataset with real-world data.

Usage:
    python dataset/dataset_from_images.py --input_dir path/to/images --output dataset/crowd_dataset.csv

The script can auto-label based on people count, or you can provide
labels manually.
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
    Automatically assign a density label based on spatial features.

    Args:
        features: Dictionary of extracted spatial features.

    Returns:
        Density label string.
    """
    people_count = int(features.get("people_count", 0))
    occupancy = float(features.get("occupancy_ratio", 0.0))
    avg_dist = float(features.get("avg_distance", 1.0))

    if people_count == 0:
        return "LOW"

    # High density if many people, high area coverage, or tightly packed
    if people_count >= 15 or occupancy > 0.4 or (people_count >= 8 and avg_dist < 0.1):
        return "HIGH"
    # Medium density if moderate count, moderate coverage, or somewhat packed
    elif people_count >= 6 or occupancy > 0.15 or (people_count >= 3 and avg_dist < 0.2):
        return "MEDIUM"
    else:
        return "LOW"


def process_images(
    input_dir: str,
    output_path: str | None = None,
    append: bool = True,
    confidence: float = 0.3,
) -> pd.DataFrame:
    """
    Process all images in a directory and generate dataset rows.

    Args:
        input_dir: Directory containing images (JPG, JPEG, PNG).
        output_path: Path for the output CSV. Defaults to dataset/crowd_dataset.csv.
        append: If True, append to existing CSV. If False, overwrite.
        confidence: Detection confidence threshold.

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

    print(f"Processing {len(image_files)} images...")

    rows = []
    for i, img_path in enumerate(image_files):
        print(f"  [{i+1}/{len(image_files)}] {os.path.basename(img_path)}...", end=" ")

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

            # Auto-label
            features["density_label"] = auto_label(features)
            features["source_file"] = os.path.basename(img_path)

            rows.append(features)
            print(f"→ {int(features['people_count'])} people, {features['density_label']}")

        except Exception as e:
            print(f"ERROR ({e})")
            continue

    new_df = pd.DataFrame(rows)

    if len(new_df) == 0:
        print("No valid images processed.")
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

    args = parser.parse_args()
    process_images(
        input_dir=args.input_dir,
        output_path=args.output,
        append=not args.overwrite,
        confidence=args.confidence,
    )
