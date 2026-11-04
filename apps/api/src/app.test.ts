import { test } from "node:test";
import assert from "node:assert/strict";
import { buildApp } from "./app.ts";
import { verifyMagicBytes } from "./storage.ts";

const TEST_ENV = {
  NODE_ENV: "test" as const,
  PORT: 4099,
  DATABASE_URL:
    process.env.DATABASE_URL ??
    "postgres://visionlytics:visionlytics_dev_pw@127.0.0.1:5432/visionlytics",
  REDIS_URL: process.env.REDIS_URL ?? "redis://127.0.0.1:6379",
  ML_URL: process.env.ML_URL ?? "http://127.0.0.1:8000",
  S3_ENDPOINT: process.env.S3_ENDPOINT ?? "http://127.0.0.1:9000",
  S3_ACCESS_KEY: "minioadmin",
  S3_SECRET_KEY: "minioadmin_dev_pw",
  S3_BUCKET: "visionlytics-media",
  CORS_ORIGINS: "http://localhost:5173",
};

test("verifyMagicBytes validates JPEG, PNG, and MP4 signatures", () => {
  assert.equal(verifyMagicBytes(new Uint8Array([0xff, 0xd8, 0xff, 0xe0]), "image/jpeg"), true);
  assert.equal(verifyMagicBytes(new Uint8Array([0x89, 0x50, 0x4e, 0x47]), "image/png"), true);
  assert.equal(
    verifyMagicBytes(
      new Uint8Array([0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70]),
      "video/mp4",
    ),
    true,
  );
  assert.equal(verifyMagicBytes(new Uint8Array([0x00, 0x01, 0x02, 0x03]), "image/jpeg"), false);
});

test("OpenAPI 3.1 contract, RBAC, tenant isolation, presigned S3 upload, and idempotent BullMQ queueing", async () => {
  const runtime = await buildApp(TEST_ENV);
  const { app, sql } = runtime;
  try {
    // 1. Verify OpenAPI 3.1 spec is generated
    const specRes = await app.inject({ method: "GET", url: "/docs/json" });
    assert.equal(specRes.statusCode, 200);
    const spec = specRes.json() as { openapi: string; paths: Record<string, unknown> };
    assert.equal(spec.openapi, "3.1.0");
    assert.ok("/v1/auth/register" in spec.paths);
    assert.ok("/v1/analyses" in spec.paths);

    // 2. Verify TimescaleDB hypertable exists on frame_events
    const hyper = await sql`
      SELECT hypertable_name FROM timescaledb_information.hypertables
      WHERE hypertable_name = 'frame_events'
    `;
    assert.equal(hyper.length, 1);

    // 3. Register Tenant A and Tenant B
    const slugA = `org-a-${Date.now()}`;
    const regA = await app.inject({
      method: "POST",
      url: "/v1/auth/register",
      payload: {
        email: `${slugA}@example.com`,
        password: "correct-horse-battery",
        name: "Alice Owner",
        orgName: "Optics Lab A",
        orgSlug: slugA,
      },
    });
    assert.equal(regA.statusCode, 201);
    const bodyA = regA.json() as { token: string; org: { id: string } };

    const slugB = `org-b-${Date.now()}`;
    const regB = await app.inject({
      method: "POST",
      url: "/v1/auth/register",
      payload: {
        email: `${slugB}@example.com`,
        password: "correct-horse-battery",
        name: "Bob Owner",
        orgName: "Optics Lab B",
        orgSlug: slugB,
      },
    });
    assert.equal(regB.statusCode, 201);
    const bodyB = regB.json() as { token: string; org: { id: string } };

    // 4. Create project in Tenant A
    const projRes = await app.inject({
      method: "POST",
      url: "/v1/projects",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        name: "North Gate Dock",
        description: "60fps loading bay camera",
        privacyMode: true,
      },
    });
    assert.equal(projRes.statusCode, 201);
    const projA = projRes.json() as { id: string };

    // 5. Verify Tenant B cannot see Tenant A's project
    const listB = await app.inject({
      method: "GET",
      url: "/v1/projects",
      headers: { authorization: `Bearer ${bodyB.token}` },
    });
    assert.equal(listB.statusCode, 200);
    const itemsB = (listB.json() as { items: Array<{ id: string }> }).items;
    assert.equal(itemsB.some((p) => p.id === projA.id), false);

    // 6. Verify viewer API key cannot create projects (RBAC enforcement)
    const keyRes = await app.inject({
      method: "POST",
      url: "/v1/api-keys",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: { name: "Read-only dashboard key", role: "viewer" },
    });
    assert.equal(keyRes.statusCode, 201);
    const viewerKey = (keyRes.json() as { secretKey: string }).secretKey;

    const viewerWrite = await app.inject({
      method: "POST",
      url: "/v1/projects",
      headers: { "x-api-key": viewerKey },
      payload: { name: "Unauthorized project" },
    });
    assert.equal(viewerWrite.statusCode, 403);

    const viewerRead = await app.inject({
      method: "GET",
      url: "/v1/projects",
      headers: { "x-api-key": viewerKey },
    });
    assert.equal(viewerRead.statusCode, 200);

    // 7. Presign media upload and reject invalid MIME
    const badMime = await app.inject({
      method: "POST",
      url: "/v1/media/presign",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        filename: "malware.exe",
        mimeType: "application/x-msdownload",
        sizeBytes: 1024,
        kind: "video",
      },
    });
    assert.equal(badMime.statusCode, 415);

    const presignRes = await app.inject({
      method: "POST",
      url: "/v1/media/presign",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        filename: "dock-clip.mp4",
        mimeType: "video/mp4",
        sizeBytes: 48_000,
        kind: "video",
      },
    });
    assert.equal(presignRes.statusCode, 201);
    const { media: mediaRow, uploadUrl } = presignRes.json() as {
      media: { id: string };
      uploadUrl: string;
    };
    assert.match(uploadUrl, /^http/);

    // 8. Enqueue analysis and verify idempotency deduplication
    const idemKey = `idem-${Date.now()}`;
    const an1 = await app.inject({
      method: "POST",
      url: "/v1/analyses",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        mediaId: mediaRow.id,
        idempotencyKey: idemKey,
      },
    });
    assert.equal(an1.statusCode, 201);
    const an1Body = an1.json() as { analysis: { id: string }; deduplicated: boolean };
    assert.equal(an1Body.deduplicated, false);

    const an2 = await app.inject({
      method: "POST",
      url: "/v1/analyses",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        mediaId: mediaRow.id,
        idempotencyKey: idemKey,
      },
    });
    assert.equal(an2.statusCode, 200);
    const an2Body = an2.json() as { analysis: { id: string }; deduplicated: boolean };
    assert.equal(an2Body.deduplicated, true);
    assert.equal(an2Body.analysis.id, an1Body.analysis.id);

    // 9. Phase 5: Polygon Zone, Alert Rule, Event Search, and CSV Report Export
    const zoneRes = await app.inject({
      method: "POST",
      url: "/v1/zones",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        name: "Boarding Zone A",
        kind: "polygon",
        points: [
          { x: 0.05, y: 0.2 },
          { x: 0.95, y: 0.2 },
          { x: 0.95, y: 0.95 },
          { x: 0.05, y: 0.95 },
        ],
      },
    });
    assert.equal(zoneRes.statusCode, 201);

    const alertRes = await app.inject({
      method: "POST",
      url: "/v1/alerts",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        projectId: projA.id,
        name: "Crowd >= 2",
        ruleType: "crowd_limit",
        condition: { maxPeople: 2 },
      },
    });
    assert.equal(alertRes.statusCode, 201);

    const csvRes = await app.inject({
      method: "GET",
      url: "/v1/reports/export?format=csv",
      headers: { authorization: `Bearer ${bodyA.token}` },
    });
    assert.equal(csvRes.statusCode, 200);
    assert.match(csvRes.headers["content-type"] as string, /text\/csv/);

    // 10. Phase 6: Dataset Creation, Training Run, and Model Promotion Gate
    const dsRes = await app.inject({
      method: "POST",
      url: "/v1/datasets",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        name: "Gate Crowd Dataset",
        format: "coco",
        classes: ["person", "bus"],
        itemCount: 32,
      },
    });
    assert.equal(dsRes.statusCode, 201);
    const ds = dsRes.json() as { id: string };

    const trRes = await app.inject({
      method: "POST",
      url: "/v1/training-runs",
      headers: { authorization: `Bearer ${bodyA.token}` },
      payload: {
        datasetId: ds.id,
        baseArchitecture: "rtdetr-v2-r18vd",
        preset: "balanced",
        epochs: 8,
      },
    });
    assert.equal(trRes.statusCode, 201);
    const { model: candModel } = trRes.json() as { model: { id: string } };

    const promRes = await app.inject({
      method: "POST",
      url: `/v1/models/${candModel.id}/promote`,
      headers: { authorization: `Bearer ${bodyA.token}` },
    });
    assert.equal(promRes.statusCode, 200);
    const promBody = promRes.json() as { gatePassed: boolean; model: { stage: string } };
    assert.equal(promBody.gatePassed, true);
    assert.equal(promBody.model.stage, "production");
  } finally {
    await runtime.close();
  }
});
