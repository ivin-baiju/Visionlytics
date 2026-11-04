import { z } from "zod";

export const BoundingBoxSchema = z.object({
  x1: z.number(),
  y1: z.number(),
  x2: z.number(),
  y2: z.number(),
});

export const ColourSwatchSchema = z.object({
  name: z.string(),
  hex: z.string().regex(/^#[0-9a-fA-F]{6}$/),
  share: z.number().min(0).max(1),
});

export const DetectionEventSchema = z.object({
  trackId: z.number().int().nonnegative().nullable(),
  label: z.string(),
  confidence: z.number().min(0).max(1),
  uncertain: z.boolean(),
  bbox: BoundingBoxSchema,
  colours: z.array(ColourSwatchSchema),
  upperClothingColours: z.array(ColourSwatchSchema).optional(),
  lowerClothingColours: z.array(ColourSwatchSchema).optional(),
});

export const HealthCheckSchema = z.object({
  name: z.string(),
  ok: z.boolean(),
  latencyMs: z.number().nonnegative(),
  error: z.string().optional(),
});

export const ReadyResponseSchema = z.object({
  status: z.enum(["ready", "degraded"]),
  checks: z.array(HealthCheckSchema),
});

export type BoundingBox = z.infer<typeof BoundingBoxSchema>;
export type ColourSwatch = z.infer<typeof ColourSwatchSchema>;
export type DetectionEvent = z.infer<typeof DetectionEventSchema>;
export type HealthCheck = z.infer<typeof HealthCheckSchema>;
export type ReadyResponse = z.infer<typeof ReadyResponseSchema>;
export { VisionlyticsClient, type VisionlyticsClientConfig, type InferFrameRequest, type InferFrameResponse } from "./sdk.ts";
