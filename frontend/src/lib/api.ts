import { FrameAnalysisResult, DatasetInfo, ModelMetric } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/py";

export class ApiOfflineError extends Error {
  constructor(message = "Backend unreachable") {
    super(message);
    this.name = "ApiOfflineError";
  }
}

async function fetchJson<T>(url: string, init?: RequestInit, timeoutMs = 8000): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return (await res.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Check if the FastAPI backend microservice is online.
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      method: "GET",
      cache: "no-store",
      signal: AbortSignal.timeout(2500),
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Send an image blob / file to the backend for frame analysis.
 * Throws ApiOfflineError when the backend is unreachable — callers must
 * surface an offline banner instead of rendering fabricated detections.
 */
export async function analyzeFrameApi(
  imageBlob: Blob,
  confidence: number = 0.3,
  track: boolean = false,
  attributes: boolean = false
): Promise<FrameAnalysisResult> {
  const formData = new FormData();
  formData.append("file", imageBlob, "frame.jpg");

  const query = new URLSearchParams();
  if (confidence !== 0.3) query.append("confidence", confidence.toString());
  if (track) query.append("track", "true");
  if (attributes) query.append("attributes", "true");

  const url = `${API_BASE}/analyze/frame?${query.toString()}`;

  try {
    return await fetchJson<FrameAnalysisResult>(url, { method: "POST", body: formData }, 30000);
  } catch (err) {
    throw err instanceof Error && err.message.startsWith("HTTP error")
      ? err
      : new ApiOfflineError(`Frame analysis failed: ${err instanceof Error ? err.message : String(err)}`);
  }
}

/**
 * Explicit demo fallback for offline development. Never used implicitly —
 * pages must only call this behind a "Demo mode" toggle with a watermark.
 */
export function createSimulatedResult(confidence: number = 0.3): FrameAnalysisResult {
  const count = Math.floor(Math.random() * 8) + 3;
  const detections = Array.from({ length: count }, (_, i) => {
    const w = Math.floor(Math.random() * 80) + 60;
    const h = Math.floor(Math.random() * 140) + 120;
    const x = Math.floor(Math.random() * (640 - w));
    const y = Math.floor(Math.random() * (480 - h));
    return {
      bbox: [x, y, x + w, y + h] as [number, number, number, number],
      confidence: Math.round((Math.random() * 0.4 + 0.55) * 100) / 100,
      class_id: 0,
      person_id: i + 1,
    };
  });

  const label = count > 8 ? "HIGH" : count > 4 ? "MEDIUM" : "LOW";
  return {
    density_label: label,
    confidence: 0.88,
    probabilities: {
      LOW: label === "LOW" ? 0.82 : 0.1,
      MEDIUM: label === "MEDIUM" ? 0.78 : 0.15,
      HIGH: label === "HIGH" ? 0.85 : 0.05,
    },
    people_count: count,
    detections,
    attributes: detections.map(() => ({
      hair_color: ["Black", "Brown", "Blonde"][Math.floor(Math.random() * 3)],
      clothing_color: ["Blue", "Dark", "White", "Red"][Math.floor(Math.random() * 4)],
      hair_confidence: 0.85,
      clothing_confidence: 0.9,
      apparent_sex: "UNKNOWN",
    })),
    tracking: true,
    features: {
      people_count: count,
      occupancy_ratio: 0.28,
      avg_person_area: 0.04,
      avg_distance: 0.35,
      min_distance: 0.12,
      spatial_spread: 0.15,
      top_region_count: Math.floor(count * 0.3),
      middle_region_count: Math.floor(count * 0.4),
      bottom_region_count: Math.ceil(count * 0.3),
      frame_occupancy_density: 0.45,
    },
    model_name: "Random Forest (Champion Fallback)",
  };
}

interface ModelsEvaluationResponse {
  val_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
  test_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
  best_model_name?: string;
}

export async function getModelsEvaluationApi(): Promise<ModelMetric[]> {
  const data = await fetchJson<ModelsEvaluationResponse>(`${API_BASE}/models/evaluation`);
  // Backend shape: { val_metrics: { [name]: { accuracy, f1_weighted, ... } }, best_model_name }
  const metrics = data.test_metrics && Object.keys(data.test_metrics).length > 0 ? data.test_metrics : data.val_metrics;
  const champion = (data.best_model_name || "Random Forest").toLowerCase();
  return Object.entries(metrics).map(([name, m]) => ({
    name,
    accuracy: m.accuracy ?? 0,
    precision: m.precision_weighted ?? 0,
    recall: m.recall_weighted ?? 0,
    f1: m.f1_weighted ?? 0,
    is_champion: name.toLowerCase() === champion,
  }));
}

export async function getModelsEvaluationApiSafe(): Promise<{ models: ModelMetric[]; offline: boolean }> {
  try {
    return { models: await getModelsEvaluationApi(), offline: false };
  } catch {
    return { models: [], offline: true };
  }
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  desc?: string;
}

export async function getModelsFeatureImportanceApi(modelName?: string): Promise<{ model_name: string; importances: FeatureImportanceItem[] }> {
  const q = modelName ? `?model_name=${encodeURIComponent(modelName)}` : "";
  const data = await fetchJson<{ model_name: string; feature_names: string[]; importances: number[] }>(
    `${API_BASE}/models/feature-importance${q}`
  );
  const total = data.importances.reduce((s, v) => s + Math.abs(v), 0) || 1;
  return {
    model_name: data.model_name,
    importances: data.feature_names.map((f, i) => ({
      feature: f,
      importance: Math.abs(data.importances[i] ?? 0) / total,
    })),
  };
}

export interface RetrainResponse {
  best_model_name: string;
  val_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
  test_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
}

export async function triggerModelsRetrainApi(): Promise<RetrainResponse> {
  try {
    // Synchronous on the backend and slow (minutes) — allow a long timeout.
    return await fetchJson<RetrainResponse>(`${API_BASE}/models/train`, { method: "POST" }, 600000);
  } catch (err) {
    throw err instanceof Error && err.message.startsWith("HTTP error")
      ? err
      : new ApiOfflineError(`Retrain request failed: ${err instanceof Error ? err.message : String(err)}`);
  }
}

export interface DatasetInfoResponse {
  n_rows: number;
  n_columns: number;
  feature_columns: string[];
  class_labels: string[];
  class_counts: Record<string, number>;
  missing_values: number;
}

export async function getDatasetInfoApi(): Promise<DatasetInfoResponse> {
  return fetchJson<DatasetInfoResponse>(`${API_BASE}/dataset/info`);
}

export interface DatasetPreviewResponse extends DatasetInfoResponse {
  columns: string[];
  rows: (number | string)[][];
  n_preview_rows: number;
}

export async function getDatasetPreviewApi(limit = 50): Promise<DatasetPreviewResponse> {
  return fetchJson<DatasetPreviewResponse>(`${API_BASE}/dataset/preview?limit=${limit}`);
}

export async function triggerDatasetGenerateApi(nPerClass = 500): Promise<DatasetPreviewResponse> {
  try {
    return await fetchJson<DatasetPreviewResponse>(`${API_BASE}/dataset/generate?n_per_class=${nPerClass}`, { method: "POST" }, 120000);
  } catch (err) {
    throw err instanceof Error && err.message.startsWith("HTTP error")
      ? err
      : new ApiOfflineError(`Dataset generation failed: ${err instanceof Error ? err.message : String(err)}`);
  }
}
