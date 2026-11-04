import { test } from "node:test";
import assert from "node:assert/strict";
import { DetectionEventSchema } from "./index.ts";

test("DetectionEventSchema validates calibrated detection payload", () => {
  const parsed = DetectionEventSchema.parse({
    trackId: 12,
    label: "person",
    confidence: 0.84,
    uncertain: false,
    bbox: { x1: 10, y1: 20, x2: 110, y2: 260 },
    colours: [{ name: "Navy", hex: "#1f2a4a", share: 0.62 }],
  });
  assert.equal(parsed.trackId, 12);
});
