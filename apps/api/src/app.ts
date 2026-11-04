import Fastify, { type FastifyInstance } from "fastify";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import swagger from "@fastify/swagger";
import swaggerUi from "@fastify/swagger-ui";
import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import { and, desc, eq, gte, lte } from "drizzle-orm";
import { Redis } from "ioredis";
import { z } from "zod";
import { type Env } from "./env.ts";
import { probe } from "./health.ts";
import * as schema from "./db/schema.ts";
import {
  generateApiKey,
  generateSessionToken,
  hashPassword,
  requireRole,
  verifyPassword,
} from "./auth.ts";
import {
  ALLOWED_MIME_TYPES,
  createPresignedPlaybackUrl,
  createPresignedUploadUrl,
  createStorageClient,
  ensureBucket,
  MAX_UPLOAD_BYTES,
} from "./storage.ts";
import { createJobQueues } from "./queues.ts";

export interface AppRuntime {
  app: FastifyInstance;
  sql: postgres.Sql;
  close: () => Promise<void>;
}

export async function buildApp(env: Env): Promise<AppRuntime> {
  const app = Fastify({
    logger: {
      level: env.NODE_ENV === "production" ? "info" : env.NODE_ENV === "test" ? "silent" : "debug",
      redact: ["req.headers.authorization", "req.headers.cookie", "req.headers['x-api-key']"],
    },
  });

  const sql = postgres(env.DATABASE_URL, { max: 10, idle_timeout: 20 });
  const db = drizzle(sql, { schema });
  const redis = new Redis(env.REDIS_URL, { lazyConnect: true, maxRetriesPerRequest: 1 });
  const queues = createJobQueues(env.REDIS_URL);
  const s3 = createStorageClient({
    endpoint: env.S3_ENDPOINT,
    accessKeyId: env.S3_ACCESS_KEY,
    secretAccessKey: env.S3_SECRET_KEY,
    bucket: env.S3_BUCKET,
  });

  await schema.runMigrations(sql);
  try {
    await ensureBucket(s3, env.S3_BUCKET);
  } catch (err) {
    app.log.warn({ err }, "bucket initialization deferred");
  }

  await app.register(helmet, { contentSecurityPolicy: false });
  await app.register(cors, { origin: env.CORS_ORIGINS.split(","), credentials: true });
  await app.register(rateLimit, { max: 300, timeWindow: "1 minute" });

  await app.register(swagger, {
    openapi: {
      openapi: "3.1.0",
      info: {
        title: "Visionlytics API",
        version: "0.2.0",
        description:
          "Production-grade computer vision telemetry, tracking, CIELAB colour classification, and model training API.",
      },
      components: {
        securitySchemes: {
          bearerAuth: { type: "http", scheme: "bearer" },
          apiKeyAuth: { type: "apiKey", in: "header", name: "x-api-key" },
        },
      },
    },
  });

  await app.register(swaggerUi, {
    routePrefix: "/docs",
  });

  const writeAudit = async (
    orgId: string,
    actorUserId: string | null,
    action: string,
    resourceType: string,
    resourceId: string,
    metadata: Record<string, unknown> = {},
  ) => {
    await db.insert(schema.auditLogs).values({
      orgId,
      actorUserId,
      action,
      resourceType,
      resourceId,
      metadata,
    });
  };

  app.get(
    "/healthz",
    { schema: { tags: ["System"], summary: "Liveness check" } },
    async () => ({ status: "ok" }),
  );

  app.get(
    "/readyz",
    { schema: { tags: ["System"], summary: "Readiness probe across all backing stores" } },
    async (_req, reply) => {
      const checks = await Promise.all([
        probe("postgres", () => sql`select 1`),
        probe("timescaledb", async () => {
          const [row] = await sql`select extversion from pg_extension where extname = 'timescaledb'`;
          if (!row) throw new Error("extension not installed");
        }),
        probe("redis", async () => {
          if (redis.status === "wait") await redis.connect();
          await redis.ping();
        }),
        probe("ml", async () => {
          const r = await fetch(`${env.ML_URL}/healthz`);
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
        }),
        probe("object-storage", async () => {
          const r = await fetch(`${env.S3_ENDPOINT}/status`);
          if (r.status >= 500) throw new Error(`HTTP ${r.status}`);
        }),
      ]);
      const ok = checks.every((c) => c.ok);
      return reply.code(ok ? 200 : 503).send({ status: ok ? "ready" : "degraded", checks });
    },
  );

  // --- Auth & Organization Onboarding ---
  const RegisterBody = z.object({
    email: z.email(),
    password: z.string().min(8).max(128),
    name: z.string().min(1).max(120),
    orgName: z.string().min(1).max(120),
    orgSlug: z
      .string()
      .min(2)
      .max(64)
      .regex(/^[a-z0-9-]+$/),
  });

  app.post(
    "/v1/auth/register",
    { schema: { tags: ["Auth"], summary: "Create user, organization, and session" } },
    async (req, reply) => {
      const parsed = RegisterBody.safeParse(req.body);
      if (!parsed.success) {
        return reply.code(400).send({ error: parsed.error.issues[0]?.message ?? "Invalid body" });
      }
      const { email, password, name, orgName, orgSlug } = parsed.data;
      const { hash, salt } = hashPassword(password);

      try {
        const [user] = await db
          .insert(schema.users)
          .values({ email: email.toLowerCase(), name, passwordHash: hash, passwordSalt: salt })
          .returning();
        if (!user) throw new Error("User creation failed");

        const [org] = await db
          .insert(schema.orgs)
          .values({ name: orgName, slug: orgSlug })
          .returning();
        if (!org) throw new Error("Org creation failed");

        await db.insert(schema.orgMembers).values({
          orgId: org.id,
          userId: user.id,
          role: "owner",
        });

        const token = generateSessionToken();
        const expiresAt = new Date(Date.now() + 7 * 24 * 3600 * 1000);
        await db.insert(schema.sessions).values({
          tokenHash: token.hash,
          userId: user.id,
          orgId: org.id,
          expiresAt,
        });

        await writeAudit(org.id, user.id, "org.created", "org", org.id, { slug: org.slug });

        return reply.code(201).send({
          token: token.raw,
          user: { id: user.id, email: user.email, name: user.name },
          org: { id: org.id, name: org.name, slug: org.slug, role: "owner" },
        });
      } catch (err) {
        return reply.code(409).send({ error: (err as Error).message });
      }
    },
  );

  const LoginBody = z.object({
    email: z.email(),
    password: z.string().min(1),
  });

  app.post(
    "/v1/auth/login",
    { schema: { tags: ["Auth"], summary: "Sign in with email and password" } },
    async (req, reply) => {
      const parsed = LoginBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid credentials payload" });

      const [user] = await db
        .select()
        .from(schema.users)
        .where(eq(schema.users.email, parsed.data.email.toLowerCase()))
        .limit(1);

      if (!user || !verifyPassword(parsed.data.password, user.passwordHash, user.passwordSalt)) {
        return reply.code(401).send({ error: "Invalid email or password" });
      }

      const [membership] = await db
        .select()
        .from(schema.orgMembers)
        .where(eq(schema.orgMembers.userId, user.id))
        .limit(1);
      if (!membership) return reply.code(403).send({ error: "No organization membership" });

      const [org] = await db
        .select()
        .from(schema.orgs)
        .where(eq(schema.orgs.id, membership.orgId))
        .limit(1);
      if (!org) return reply.code(404).send({ error: "Organization not found" });

      const token = generateSessionToken();
      const expiresAt = new Date(Date.now() + 7 * 24 * 3600 * 1000);
      await db.insert(schema.sessions).values({
        tokenHash: token.hash,
        userId: user.id,
        orgId: org.id,
        expiresAt,
      });

      return reply.send({
        token: token.raw,
        user: { id: user.id, email: user.email, name: user.name },
        org: { id: org.id, name: org.name, slug: org.slug, role: membership.role },
      });
    },
  );

  app.get(
    "/v1/auth/me",
    { schema: { tags: ["Auth"], summary: "Inspect current caller identity and tenant" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const [org] = await db
        .select()
        .from(schema.orgs)
        .where(eq(schema.orgs.id, ctx.orgId))
        .limit(1);
      return reply.send({ auth: ctx, org });
    },
  );

  // --- API Keys ---
  const CreateApiKeyBody = z.object({
    name: z.string().min(1).max(100),
    role: z.enum(["owner", "admin", "member", "viewer"]).default("member"),
  });

  app.post(
    "/v1/api-keys",
    { schema: { tags: ["API Keys"], summary: "Create hashed API key for organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "admin")(req, reply);
      if (!ctx) return;
      const parsed = CreateApiKeyBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid API key body" });

      const generated = generateApiKey();
      const [row] = await db
        .insert(schema.apiKeys)
        .values({
          orgId: ctx.orgId,
          name: parsed.data.name,
          keyPrefix: generated.prefix,
          keyHash: generated.hash,
          role: parsed.data.role,
        })
        .returning();
      if (!row) return reply.code(500).send({ error: "Failed to persist API key" });

      await writeAudit(ctx.orgId, ctx.userId, "api_key.created", "api_key", row.id, {
        name: row.name,
        role: row.role,
      });

      return reply.code(201).send({
        id: row.id,
        name: row.name,
        keyPrefix: row.keyPrefix,
        role: row.role,
        secretKey: generated.raw,
        createdAt: row.createdAt,
      });
    },
  );

  app.get(
    "/v1/api-keys",
    { schema: { tags: ["API Keys"], summary: "List active API keys for caller organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const rows = await db
        .select({
          id: schema.apiKeys.id,
          name: schema.apiKeys.name,
          keyPrefix: schema.apiKeys.keyPrefix,
          role: schema.apiKeys.role,
          lastUsedAt: schema.apiKeys.lastUsedAt,
          revokedAt: schema.apiKeys.revokedAt,
          createdAt: schema.apiKeys.createdAt,
        })
        .from(schema.apiKeys)
        .where(eq(schema.apiKeys.orgId, ctx.orgId))
        .orderBy(desc(schema.apiKeys.createdAt));
      return reply.send({ items: rows });
    },
  );

  // --- Projects ---
  const CreateProjectBody = z.object({
    name: z.string().min(1).max(120),
    description: z.string().max(500).default(""),
    privacyMode: z.boolean().default(true),
  });

  app.post(
    "/v1/projects",
    { schema: { tags: ["Projects"], summary: "Create a project inside the caller organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "member")(req, reply);
      if (!ctx) return;
      const parsed = CreateProjectBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid project payload" });

      const [project] = await db
        .insert(schema.projects)
        .values({
          orgId: ctx.orgId,
          name: parsed.data.name,
          description: parsed.data.description,
          privacyMode: parsed.data.privacyMode,
        })
        .returning();
      if (!project) return reply.code(500).send({ error: "Project creation failed" });

      await writeAudit(ctx.orgId, ctx.userId, "project.created", "project", project.id, {
        name: project.name,
      });
      return reply.code(201).send(project);
    },
  );

  app.get(
    "/v1/projects",
    { schema: { tags: ["Projects"], summary: "List projects scoped to the caller organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const items = await db
        .select()
        .from(schema.projects)
        .where(eq(schema.projects.orgId, ctx.orgId))
        .orderBy(desc(schema.projects.createdAt));
      return reply.send({ items });
    },
  );

  // --- Media & Presigned Uploads ---
  const PresignUploadBody = z.object({
    projectId: z.uuid(),
    filename: z.string().min(1).max(255),
    mimeType: z.string(),
    sizeBytes: z.number().int().positive().max(MAX_UPLOAD_BYTES),
    kind: z.enum(["image", "video", "stream"]).default("video"),
  });

  app.post(
    "/v1/media/presign",
    { schema: { tags: ["Media"], summary: "Request a presigned S3 upload URL and register media" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "member")(req, reply);
      if (!ctx) return;
      const parsed = PresignUploadBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid upload request" });

      if (!ALLOWED_MIME_TYPES.has(parsed.data.mimeType)) {
        return reply.code(415).send({ error: `Unsupported MIME type: ${parsed.data.mimeType}` });
      }

      const [project] = await db
        .select()
        .from(schema.projects)
        .where(
          and(
            eq(schema.projects.id, parsed.data.projectId),
            eq(schema.projects.orgId, ctx.orgId),
          ),
        )
        .limit(1);
      if (!project) return reply.code(404).send({ error: "Project not found in organization" });

      const safeName = parsed.data.filename.replace(/[^a-zA-Z0-9._-]/g, "_");
      const storageKey = `${ctx.orgId}/${project.id}/${Date.now()}-${safeName}`;

      const [mediaRow] = await db
        .insert(schema.media)
        .values({
          orgId: ctx.orgId,
          projectId: project.id,
          kind: parsed.data.kind,
          filename: parsed.data.filename,
          mimeType: parsed.data.mimeType,
          sizeBytes: parsed.data.sizeBytes,
          storageKey,
          status: "uploading",
        })
        .returning();
      if (!mediaRow) return reply.code(500).send({ error: "Failed to register media" });

      const uploadUrl = await createPresignedUploadUrl(
        s3,
        env.S3_BUCKET,
        storageKey,
        parsed.data.mimeType,
      );

      await writeAudit(ctx.orgId, ctx.userId, "media.presigned", "media", mediaRow.id, {
        filename: mediaRow.filename,
        sizeBytes: mediaRow.sizeBytes,
      });

      return reply.code(201).send({ media: mediaRow, uploadUrl });
    },
  );

  app.post(
    "/v1/media/:mediaId/complete",
    { schema: { tags: ["Media"], summary: "Mark uploaded media as ready and return signed playback URL" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "member")(req, reply);
      if (!ctx) return;
      const { mediaId } = req.params as { mediaId: string };
      const [row] = await db
        .update(schema.media)
        .set({ status: "ready" })
        .where(and(eq(schema.media.id, mediaId), eq(schema.media.orgId, ctx.orgId)))
        .returning();
      if (!row) return reply.code(404).send({ error: "Media not found" });

      const playbackUrl = await createPresignedPlaybackUrl(s3, env.S3_BUCKET, row.storageKey);
      return reply.send({ media: row, playbackUrl });
    },
  );

  app.get(
    "/v1/media",
    { schema: { tags: ["Media"], summary: "List media items in organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const items = await db
        .select()
        .from(schema.media)
        .where(eq(schema.media.orgId, ctx.orgId))
        .orderBy(desc(schema.media.createdAt));
      return reply.send({ items });
    },
  );

  // --- Analyses & Idempotent Job Queueing ---
  const CreateAnalysisBody = z.object({
    projectId: z.uuid(),
    mediaId: z.uuid(),
    idempotencyKey: z.string().min(4).max(128),
    config: z
      .object({
        confidenceThreshold: z.number().min(0.05).max(0.99).default(0.5),
        privacyMode: z.boolean().default(true),
        tiledInference: z.boolean().default(false),
        openVocabPrompts: z.array(z.string()).default([]),
      })
      .default({
        confidenceThreshold: 0.5,
        privacyMode: true,
        tiledInference: false,
        openVocabPrompts: [],
      }),
  });

  app.post(
    "/v1/analyses",
    {
      schema: {
        tags: ["Analyses"],
        summary: "Enqueue an idempotent frame/video analysis job on BullMQ",
      },
    },
    async (req, reply) => {
      const ctx = await requireRole(db, "member")(req, reply);
      if (!ctx) return;
      const parsed = CreateAnalysisBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid analysis payload" });

      const [existing] = await db
        .select()
        .from(schema.analyses)
        .where(
          and(
            eq(schema.analyses.orgId, ctx.orgId),
            eq(schema.analyses.idempotencyKey, parsed.data.idempotencyKey),
          ),
        )
        .limit(1);
      if (existing) {
        return reply.code(200).send({ analysis: existing, deduplicated: true });
      }

      const [mediaRow] = await db
        .select()
        .from(schema.media)
        .where(
          and(
            eq(schema.media.id, parsed.data.mediaId),
            eq(schema.media.orgId, ctx.orgId),
          ),
        )
        .limit(1);
      if (!mediaRow) return reply.code(404).send({ error: "Media not found in organization" });

      const [analysis] = await db
        .insert(schema.analyses)
        .values({
          orgId: ctx.orgId,
          projectId: parsed.data.projectId,
          mediaId: mediaRow.id,
          idempotencyKey: parsed.data.idempotencyKey,
          config: parsed.data.config,
          status: "queued",
        })
        .returning();
      if (!analysis) return reply.code(500).send({ error: "Failed to create analysis" });

      await queues.analysis.add(
        "analyze-media",
        {
          analysisId: analysis.id,
          orgId: ctx.orgId,
          projectId: analysis.projectId,
          mediaId: mediaRow.id,
          storageKey: mediaRow.storageKey,
          config: parsed.data.config,
        },
        { jobId: `${ctx.orgId}_${parsed.data.idempotencyKey}` },
      );

      await writeAudit(ctx.orgId, ctx.userId, "analysis.enqueued", "analysis", analysis.id, {
        mediaId: mediaRow.id,
        idempotencyKey: parsed.data.idempotencyKey,
      });

      return reply.code(201).send({ analysis, deduplicated: false });
    },
  );

  app.get(
    "/v1/analyses",
    { schema: { tags: ["Analyses"], summary: "List analyses for caller organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const items = await db
        .select()
        .from(schema.analyses)
        .where(eq(schema.analyses.orgId, ctx.orgId))
        .orderBy(desc(schema.analyses.createdAt));
      return reply.send({ items });
    },
  );

  // --- Frame Events (TimescaleDB hypertable queries) ---
  app.get(
    "/v1/analyses/:analysisId/frames",
    {
      schema: {
        tags: ["Frames"],
        summary: "Query per-frame telemetry from the TimescaleDB frame_events hypertable",
      },
    },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const { analysisId } = req.params as { analysisId: string };
      const q = req.query as { minPeople?: string; fromFrame?: string; toFrame?: string };

      const conditions = [
        eq(schema.frameEvents.orgId, ctx.orgId),
        eq(schema.frameEvents.analysisId, analysisId),
      ];
      if (q.minPeople !== undefined) {
        conditions.push(gte(schema.frameEvents.peopleCount, Number(q.minPeople)));
      }
      if (q.fromFrame !== undefined) {
        conditions.push(gte(schema.frameEvents.frameIndex, Number(q.fromFrame)));
      }
      if (q.toFrame !== undefined) {
        conditions.push(lte(schema.frameEvents.frameIndex, Number(q.toFrame)));
      }

      const items = await db
        .select()
        .from(schema.frameEvents)
        .where(and(...conditions))
        .orderBy(schema.frameEvents.frameIndex)
        .limit(1000);
      return reply.send({ items });
    },
  );

  // --- Zones, Alerts, Datasets, Models, Audit Logs ---
  const CreateZoneBody = z.object({
    projectId: z.uuid(),
    name: z.string().min(1).max(100),
    kind: z.enum(["polygon", "line"]),
    points: z.array(z.object({ x: z.number(), y: z.number() })).min(2),
    colourHex: z.string().regex(/^#[0-9a-fA-F]{6}$/).default("#ffb21f"),
  });

  app.post(
    "/v1/zones",
    { schema: { tags: ["Zones"], summary: "Create polygon zone or counting line" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "member")(req, reply);
      if (!ctx) return;
      const parsed = CreateZoneBody.safeParse(req.body);
      if (!parsed.success) return reply.code(400).send({ error: "Invalid zone payload" });
      const [zone] = await db
        .insert(schema.zones)
        .values({ orgId: ctx.orgId, ...parsed.data })
        .returning();
      return reply.code(201).send(zone);
    },
  );

  app.get(
    "/v1/zones",
    { schema: { tags: ["Zones"], summary: "List zones for caller organization" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "viewer")(req, reply);
      if (!ctx) return;
      const items = await db
        .select()
        .from(schema.zones)
        .where(eq(schema.zones.orgId, ctx.orgId));
      return reply.send({ items });
    },
  );

  app.get(
    "/v1/audit-logs",
    { schema: { tags: ["Security"], summary: "List tenant-isolated audit trail events" } },
    async (req, reply) => {
      const ctx = await requireRole(db, "admin")(req, reply);
      if (!ctx) return;
      const items = await db
        .select()
        .from(schema.auditLogs)
        .where(eq(schema.auditLogs.orgId, ctx.orgId))
        .orderBy(desc(schema.auditLogs.createdAt))
        .limit(200);
      return reply.send({ items });
    },
  );

  const close = async () => {
    await app.close();
    await Promise.allSettled([queues.close(), sql.end({ timeout: 5 }), redis.quit()]);
  };

  return { app, sql, close };
}
