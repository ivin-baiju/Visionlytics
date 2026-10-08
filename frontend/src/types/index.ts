export type DensityLabel = "LOW" | "MEDIUM" | "HIGH";

export interface Detection {
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  confidence: number;
  class_id: number;
  person_id?: number | null;
}

export interface PersonAttribute {
  hair_color: string;
  clothing_color: string;
  hair_confidence: number;
  clothing_confidence: number;
  apparent_sex: string;
}

export interface SpatialFeatures {
  people_count: number;
  occupancy_ratio: number;
  avg_person_area: number;
  avg_distance: number;
  min_distance: number;
  std_distance: number;
  top_region_count: number;
  middle_region_count: number;
  bottom_region_count: number;
  density_ratio: number;
}

export interface FrameAnalysisResult {
  density_label: DensityLabel;
  confidence: number;
  probabilities: Record<DensityLabel, number>;
  people_count: number;
  detections: Detection[];
  attributes?: PersonAttribute[];
  tracking?: boolean;
  features: SpatialFeatures;
  model_name: string;
}

export interface ModelMetric {
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  is_champion?: boolean;
}

export interface DatasetInfo {
  total_samples: number;
  feature_names: string[];
  class_counts: Record<DensityLabel, number>;
}
