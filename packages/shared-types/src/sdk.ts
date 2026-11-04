import type { DetectionEvent, ReadyResponse } from "./index.ts";

export interface VisionlyticsClientConfig {
  baseUrl: string;
  apiKey?: string;
  bearerToken?: string;
}

export interface InferFrameRequest {
  imageBase64: string;
  preset?: "fast" | "balanced" | "max_accuracy";
  minConfidence?: number;
  uncertainThreshold?: number;
  tiled?: boolean;
  openVocabQuery?: string;
  streamId?: string;
  frameIndex?: number;
}

export interface InferFrameResponse {
  width: number;
  height: number;
  preset: string;
  architecture: string;
  latencyMs: number;
  peopleCount: number;
  uncertainCount: number;
  detections: DetectionEvent[];
  analysisId: string;
  frameIndex: number;
}

/**
 * Official TypeScript/JavaScript SDK client for the Visionlytics REST API.
 */
export class VisionlyticsClient {
  private readonly baseUrl: string;
  private readonly headers: Record<string, string>;

  constructor(cfg: VisionlyticsClientConfig) {
    this.baseUrl = cfg.baseUrl.replace(/\/$/, "");
    this.headers = { "content-type": "application/json" };
    if (cfg.apiKey) this.headers["x-api-key"] = cfg.apiKey;
    if (cfg.bearerToken) this.headers.authorization = `Bearer ${cfg.bearerToken}`;
  }

  async readyz(): Promise<ReadyResponse> {
    const r = await fetch(`${this.baseUrl}/readyz`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return (await r.json()) as ReadyResponse;
  }

  async inferFrame(req: InferFrameRequest): Promise<InferFrameResponse> {
    const r = await fetch(`${this.baseUrl}/v1/ml/infer-frame`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(req),
    });
    if (!r.ok) {
      throw new Error(`Visionlytics inferFrame failed (HTTP ${r.status}): ${await r.text()}`);
    }
    return (await r.json()) as InferFrameResponse;
  }

  async searchEvents(params: {
    minPeople?: number;
    label?: string;
    colour?: string;
    zoneId?: string;
  }): Promise<{ count: number; items: Array<Record<string, unknown>> }> {
    const qs = new URLSearchParams();
    if (params.minPeople !== undefined) qs.set("minPeople", String(params.minPeople));
    if (params.label) qs.set("label", params.label);
    if (params.colour) qs.set("colour", params.colour);
    if (params.zoneId) qs.set("zoneId", params.zoneId);
    const r = await fetch(`${this.baseUrl}/v1/events/search?${qs.toString()}`, {
      headers: this.headers,
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return (await r.json()) as { count: number; items: Array<Record<string, unknown>> };
  }
}
