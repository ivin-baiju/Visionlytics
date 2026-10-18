import { FrameAnalysisResult, DatasetInfo, ModelMetric } from "@/types";

// API base: direct backend URL when NEXT_PUBLIC_API_URL is set (Vercel prod),
// otherwise the Next.js rewrite proxy (/api/py -> localhost:8000, local dev).
// On Vercel with no backend configured, API calls 404 — pages then fall back
// to labeled DEMO_MODE content instead of showing raw errors.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/py";

export const BACKEND_CONFIGURED = Boolean(process.env.NEXT_PUBLIC_API_URL);

export class ApiOfflineError extends Error {
  status?: number;
  constructor(message = "Backend unreachable", status?: number) {
    super(message);
    this.name = "ApiOfflineError";
    this.status = status;
  }
}

async function fetchJson<T>(url: string, init?: RequestInit, timeoutMs = 8000): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    if (!res.ok) throw new ApiOfflineError(`HTTP error ${res.status}`, res.status);
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiOfflineError) throw err;
    throw new ApiOfflineError(err instanceof Error ? err.message : String(err));
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

export function isDemoMode(): boolean {
  return !BACKEND_CONFIGURED && typeof window !== "undefined" && window.location.hostname.endsWith(".vercel.app");
}

// ── Demo-mode static data (used ONLY when no backend is configured) ─────────
// These mirror the real backend shapes so charts/tables render on the
// deployed site. Every consumer must label them as demo content.

export const DEMO_MODELS: ModelMetric[] = [
  { name: "Random Forest", accuracy: 0.942, precision: 0.938, recall: 0.945, f1: 0.941, is_champion: true },
  { name: "Voting Ensemble", accuracy: 0.935, precision: 0.931, recall: 0.939, f1: 0.935 },
  { name: "Gradient Boosting", accuracy: 0.928, precision: 0.925, recall: 0.93, f1: 0.927 },
  { name: "SVM", accuracy: 0.914, precision: 0.908, recall: 0.919, f1: 0.913 },
  { name: "Logistic Regression", accuracy: 0.876, precision: 0.869, recall: 0.88, f1: 0.874 },
  { name: "KNN", accuracy: 0.862, precision: 0.855, recall: 0.867, f1: 0.861 },
  { name: "Decision Tree", accuracy: 0.841, precision: 0.835, recall: 0.848, f1: 0.841 },
];

export const DEMO_FEATURE_IMPORTANCE = {
  model_name: "Random Forest",
  importances: [
    { feature: "people_count", importance: 0.38, desc: "Primary crowd volume count" },
    { feature: "occupancy_ratio", importance: 0.22, desc: "Total pixel space coverage" },
    { feature: "avg_distance", importance: 0.14, desc: "Mean interpersonal distance" },
    { feature: "min_distance", importance: 0.11, desc: "Bottleneck cluster proximity" },
    { feature: "frame_occupancy_density", importance: 0.07, desc: "Perspective-weighted density" },
    { feature: "avg_person_area", importance: 0.05, desc: "Perspective depth indicator" },
    { feature: "spatial_spread", importance: 0.03, desc: "Dispersion standard deviation" },
  ],
};

export const DEMO_DATASET_COLUMNS = [
  "people_count", "occupancy_ratio", "avg_person_area", "avg_distance",
  "min_distance", "spatial_spread", "top_region_count", "middle_region_count",
  "bottom_region_count", "frame_occupancy_density", "density_label",
];

export const DEMO_DATASET_ROWS: (number | string)[][] = [
  [3, 0.08, 0.0267, 0.52, 0.31, 0.18, 1, 1, 1, 2.4, "LOW"],
  [4, 0.11, 0.0275, 0.44, 0.22, 0.21, 1, 2, 1, 3.1, "LOW"],
  [8, 0.24, 0.03, 0.29, 0.15, 0.28, 2, 4, 2, 9.6, "MEDIUM"],
  [11, 0.32, 0.0291, 0.23, 0.09, 0.31, 3, 5, 3, 14.2, "MEDIUM"],
  [18, 0.56, 0.0311, 0.14, 0.04, 0.36, 5, 8, 5, 28.5, "HIGH"],
  [22, 0.68, 0.0309, 0.11, 0.02, 0.38, 6, 9, 7, 36.1, "HIGH"],
  [2, 0.05, 0.025, 0.65, 0.65, 0.12, 0, 1, 1, 1.5, "LOW"],
  [9, 0.28, 0.0311, 0.26, 0.12, 0.29, 3, 4, 2, 11.8, "MEDIUM"],
];

export const DEMO_DATASET_INFO = {
  n_rows: 5001,
  n_columns: 11,
  feature_columns: DEMO_DATASET_COLUMNS.slice(0, 10),
  class_labels: ["LOW", "MEDIUM", "HIGH"],
  class_counts: { LOW: 1667, MEDIUM: 1667, HIGH: 1667 },
  missing_values: 0,
};

interface ModelsEvaluationResponse {
  val_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
  test_metrics: Record<string, { accuracy: number; f1_weighted: number; precision_weighted?: number; recall_weighted?: number }>;
  best_model_name?: string;
}

export async function getModelsEvaluationApi(): Promise<ModelMetric[]> {
  try {
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
  } catch {
    // No backend on the deployed site → labeled demo leaderboard.
    if (typeof window !== "undefined" && window.location.hostname.endsWith(".vercel.app") && !BACKEND_CONFIGURED) {
      return DEMO_MODELS;
    }
    throw new ApiOfflineError("Model metrics unavailable. Start the backend with `python start_local.py`.");
  }
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

export async function getModelsFeatureImportanceApi(modelName?: string): Promise<{ model_name: string; importances: FeatureImportanceItem[]; demo?: boolean }> {
  try {
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
  } catch {
    if (typeof window !== "undefined" && window.location.hostname.endsWith(".vercel.app") && !BACKEND_CONFIGURED) {
      return { ...DEMO_FEATURE_IMPORTANCE, demo: true };
    }
    throw new ApiOfflineError("Feature importance unavailable. Start the backend with `python start_local.py`.");
  }
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
  try {
    return await fetchJson<DatasetInfoResponse>(`${API_BASE}/dataset/info`);
  } catch {
    if (typeof window !== "undefined" && window.location.hostname.endsWith(".vercel.app") && !BACKEND_CONFIGURED) {
      return { ...DEMO_DATASET_INFO, class_counts: { ...DEMO_DATASET_INFO.class_counts } };
    }
    throw new ApiOfflineError("Dataset info unavailable. Start the backend with `python start_local.py`.");
  }
}

export interface DatasetPreviewResponse extends DatasetInfoResponse {
  columns: string[];
  rows: (number | string)[][];
  n_preview_rows: number;
}

export async function getDatasetPreviewApi(limit = 50): Promise<DatasetPreviewResponse> {
  try {
    return await fetchJson<DatasetPreviewResponse>(`${API_BASE}/dataset/preview?limit=${limit}`);
  } catch {
    if (typeof window !== "undefined" && window.location.hostname.endsWith(".vercel.app") && !BACKEND_CONFIGURED) {
      return {
        ...DEMO_DATASET_INFO,
        class_counts: { ...DEMO_DATASET_INFO.class_counts },
        columns: [...DEMO_DATASET_COLUMNS],
        rows: DEMO_DATASET_ROWS.slice(0, limit),
        n_preview_rows: Math.min(limit, DEMO_DATASET_ROWS.length),
      };
    }
    throw new ApiOfflineError("Dataset preview unavailable. Start the backend with `python start_local.py`.");
  }
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
