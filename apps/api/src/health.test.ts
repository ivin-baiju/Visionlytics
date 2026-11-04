import { test } from "node:test";
import assert from "node:assert/strict";
import { probe } from "./health.ts";

test("probe reports success with latency", async () => {
  const r = await probe("ok", async () => 1);
  assert.equal(r.ok, true);
  assert.ok(r.latencyMs >= 0);
});

test("probe reports failure message", async () => {
  const r = await probe("bad", async () => { throw new Error("refused"); });
  assert.deepEqual([r.ok, r.error], [false, "refused"]);
});

test("probe times out instead of hanging", async () => {
  const r = await probe("slow", () => new Promise((res) => setTimeout(res, 500)), 50);
  assert.equal(r.ok, false);
  assert.match(r.error ?? "", /timeout/);
});
