import { NextResponse } from "next/server";

export async function GET() {
  const modelsData = {
    best_model_name: "Random Forest",
    val_metrics: {
      "Random Forest": { accuracy: 0.948, precision_weighted: 0.945, recall_weighted: 0.948, f1_weighted: 0.946 },
      "Voting Ensemble": { accuracy: 0.941, precision_weighted: 0.938, recall_weighted: 0.941, f1_weighted: 0.939 },
      "Gradient Boosting": { accuracy: 0.933, precision_weighted: 0.930, recall_weighted: 0.933, f1_weighted: 0.931 },
      "SVM": { accuracy: 0.920, precision_weighted: 0.916, recall_weighted: 0.920, f1_weighted: 0.918 },
      "Logistic Regression": { accuracy: 0.884, precision_weighted: 0.878, recall_weighted: 0.884, f1_weighted: 0.881 },
      "KNN": { accuracy: 0.870, precision_weighted: 0.864, recall_weighted: 0.870, f1_weighted: 0.867 },
      "Decision Tree": { accuracy: 0.849, precision_weighted: 0.842, recall_weighted: 0.849, f1_weighted: 0.845 },
    },
    test_metrics: {
      "Random Forest": { accuracy: 0.942, precision_weighted: 0.938, recall_weighted: 0.942, f1_weighted: 0.940 },
      "Voting Ensemble": { accuracy: 0.935, precision_weighted: 0.931, recall_weighted: 0.935, f1_weighted: 0.933 },
      "Gradient Boosting": { accuracy: 0.928, precision_weighted: 0.925, recall_weighted: 0.928, f1_weighted: 0.926 },
      "SVM": { accuracy: 0.914, precision_weighted: 0.908, recall_weighted: 0.914, f1_weighted: 0.911 },
      "Logistic Regression": { accuracy: 0.876, precision_weighted: 0.869, recall_weighted: 0.876, f1_weighted: 0.872 },
      "KNN": { accuracy: 0.862, precision_weighted: 0.855, recall_weighted: 0.862, f1_weighted: 0.858 },
      "Decision Tree": { accuracy: 0.841, precision_weighted: 0.835, recall_weighted: 0.841, f1_weighted: 0.838 },
    },
    training_times: {
      "Random Forest": 1.42,
      "Voting Ensemble": 3.85,
      "Gradient Boosting": 2.15,
      "SVM": 0.95,
      "Logistic Regression": 0.18,
      "KNN": 0.08,
      "Decision Tree": 0.05,
    },
    class_labels: ["LOW", "MEDIUM", "HIGH"],
    feature_columns: [
      "people_count", "occupancy_ratio", "avg_person_area", "avg_distance",
      "min_distance", "spatial_spread", "top_region_count", "middle_region_count",
      "bottom_region_count", "frame_occupancy_density",
    ],
  };

  return NextResponse.json(modelsData);
}
