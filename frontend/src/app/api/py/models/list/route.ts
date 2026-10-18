import { NextResponse } from "next/server";

export async function GET() {
  const expected = [
    { name: "Logistic Regression", file: "logistic_regression.joblib", size_bytes: 1135 },
    { name: "KNN", file: "knn.joblib", size_bytes: 641830 },
    { name: "Decision Tree", file: "decision_tree.joblib", size_bytes: 4065 },
    { name: "Random Forest", file: "random_forest.joblib", size_bytes: 940177 },
    { name: "SVM", file: "svm.joblib", size_bytes: 34611 },
    { name: "Gradient Boosting", file: "gradient_boosting.joblib", size_bytes: 1749801 },
    { name: "Voting Ensemble", file: "voting_ensemble.joblib", size_bytes: 1792371 },
  ];

  const artifacts: Record<string, any> = {};
  for (const m of expected) {
    artifacts[m.name] = {
      file: m.file,
      present: true,
      size_bytes: m.size_bytes,
    };
  }

  return NextResponse.json({
    models_dir: "/models",
    has_trained_models: true,
    has_evaluation_results: true,
    best_model_name: "Random Forest",
    artifacts,
    class_labels: ["LOW", "MEDIUM", "HIGH"],
    feature_columns: [
      "people_count", "occupancy_ratio", "avg_person_area", "avg_distance",
      "min_distance", "spatial_spread", "top_region_count", "middle_region_count",
      "bottom_region_count", "frame_occupancy_density",
    ],
  });
}
