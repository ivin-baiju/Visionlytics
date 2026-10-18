import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    model_name: "Random Forest",
    feature_names: [
      "people_count",
      "occupancy_ratio",
      "avg_distance",
      "min_distance",
      "frame_occupancy_density",
      "avg_person_area",
      "spatial_spread",
    ],
    importances: [0.38, 0.22, 0.14, 0.11, 0.07, 0.05, 0.03],
  });
}
