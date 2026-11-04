import {
  bigint,
  boolean,
  doublePrecision,
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";
import type postgres from "postgres";

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  passwordHash: text("password_hash").notNull(),
  passwordSalt: text("password_salt").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const orgs = pgTable("orgs", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: text("name").notNull(),
  slug: text("slug").notNull().unique(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const orgMembers = pgTable(
  "org_members",
  {
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    role: text("role").notNull().$type<"owner" | "admin" | "member" | "viewer">(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [primaryKey({ columns: [t.orgId, t.userId] })],
);

export const sessions = pgTable("sessions", {
  id: uuid("id").defaultRandom().primaryKey(),
  tokenHash: text("token_hash").notNull().unique(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  orgId: uuid("org_id")
    .notNull()
    .references(() => orgs.id, { onDelete: "cascade" }),
  expiresAt: timestamp("expires_at", { withTimezone: true }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const projects = pgTable(
  "projects",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    description: text("description").notNull().default(""),
    privacyMode: boolean("privacy_mode").notNull().default(true),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("projects_org_idx").on(t.orgId)],
);

export const media = pgTable(
  "media",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    kind: text("kind").notNull().$type<"image" | "video" | "stream">(),
    filename: text("filename").notNull(),
    mimeType: text("mime_type").notNull(),
    sizeBytes: bigint("size_bytes", { mode: "number" }).notNull(),
    storageKey: text("storage_key").notNull(),
    status: text("status")
      .notNull()
      .$type<"uploading" | "ready" | "failed">()
      .default("uploading"),
    width: integer("width"),
    height: integer("height"),
    durationSeconds: doublePrecision("duration_seconds"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("media_org_project_idx").on(t.orgId, t.projectId)],
);

export const analyses = pgTable(
  "analyses",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    mediaId: uuid("media_id")
      .notNull()
      .references(() => media.id, { onDelete: "cascade" }),
    status: text("status")
      .notNull()
      .$type<"queued" | "running" | "completed" | "failed">()
      .default("queued"),
    idempotencyKey: text("idempotency_key").notNull(),
    config: jsonb("config").notNull().default({}),
    summary: jsonb("summary").notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    completedAt: timestamp("completed_at", { withTimezone: true }),
  },
  (t) => [index("analyses_org_media_idx").on(t.orgId, t.mediaId)],
);

/**
 * TimescaleDB hypertable partitioned on `observed_at`.
 * Composite primary key includes the time partitioning column (`observed_at`) as required by TimescaleDB.
 */
export const frameEvents = pgTable(
  "frame_events",
  {
    observedAt: timestamp("observed_at", { withTimezone: true }).notNull(),
    orgId: uuid("org_id").notNull(),
    analysisId: uuid("analysis_id").notNull(),
    frameIndex: integer("frame_index").notNull(),
    peopleCount: integer("people_count").notNull(),
    uniqueTrackIds: jsonb("unique_track_ids").notNull().$type<number[]>(),
    detections: jsonb("detections").notNull().default([]),
    zoneCounts: jsonb("zone_counts").notNull().default({}),
  },
  (t) => [
    primaryKey({ columns: [t.orgId, t.analysisId, t.frameIndex, t.observedAt] }),
    index("frame_events_org_time_idx").on(t.orgId, t.observedAt),
  ],
);

export const tracks = pgTable(
  "tracks",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id").notNull(),
    analysisId: uuid("analysis_id")
      .notNull()
      .references(() => analyses.id, { onDelete: "cascade" }),
    trackNumber: integer("track_number").notNull(),
    label: text("label").notNull(),
    firstFrame: integer("first_frame").notNull(),
    lastFrame: integer("last_frame").notNull(),
    avgConfidence: doublePrecision("avg_confidence").notNull(),
    dominantColours: jsonb("dominant_colours").notNull().default([]),
    upperClothingColours: jsonb("upper_clothing_colours").notNull().default([]),
    lowerClothingColours: jsonb("lower_clothing_colours").notNull().default([]),
    trajectory: jsonb("trajectory").notNull().default([]),
  },
  (t) => [index("tracks_org_analysis_idx").on(t.orgId, t.analysisId)],
);

export const zones = pgTable(
  "zones",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    kind: text("kind").notNull().$type<"polygon" | "line">(),
    points: jsonb("points").notNull().$type<Array<{ x: number; y: number }>>(),
    colourHex: text("colour_hex").notNull().default("#ffb21f"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("zones_org_project_idx").on(t.orgId, t.projectId)],
);

export const alerts = pgTable(
  "alerts",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    ruleType: text("rule_type")
      .notNull()
      .$type<"crowd_limit" | "zone_entry" | "loitering" | "object_match">(),
    condition: jsonb("condition").notNull(),
    channels: jsonb("channels").notNull().default([]),
    enabled: boolean("enabled").notNull().default(true),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("alerts_org_project_idx").on(t.orgId, t.projectId)],
);

export const datasets = pgTable(
  "datasets",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    format: text("format").notNull().$type<"coco" | "yolo" | "pascal">(),
    classes: jsonb("classes").notNull().$type<string[]>().default([]),
    itemCount: integer("item_count").notNull().default(0),
    healthReport: jsonb("health_report").notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("datasets_org_idx").on(t.orgId)],
);

export const annotations = pgTable(
  "annotations",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id").notNull(),
    datasetId: uuid("dataset_id")
      .notNull()
      .references(() => datasets.id, { onDelete: "cascade" }),
    mediaId: uuid("media_id")
      .notNull()
      .references(() => media.id, { onDelete: "cascade" }),
    frameIndex: integer("frame_index").notNull().default(0),
    boxes: jsonb("boxes").notNull().default([]),
    source: text("source").notNull().$type<"human" | "auto_prelabel" | "active_learning">(),
    reviewed: boolean("reviewed").notNull().default(false),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("annotations_org_dataset_idx").on(t.orgId, t.datasetId)],
);

export const trainingRuns = pgTable(
  "training_runs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    datasetId: uuid("dataset_id")
      .notNull()
      .references(() => datasets.id, { onDelete: "cascade" }),
    baseArchitecture: text("base_architecture").notNull(),
    preset: text("preset").notNull().$type<"fast" | "balanced" | "max_accuracy">(),
    status: text("status")
      .notNull()
      .$type<"queued" | "running" | "completed" | "failed" | "stopped">()
      .default("queued"),
    hyperparams: jsonb("hyperparams").notNull().default({}),
    metricsHistory: jsonb("metrics_history").notNull().default([]),
    finalMetrics: jsonb("final_metrics").notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("training_runs_org_idx").on(t.orgId)],
);

export const models = pgTable(
  "models",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    trainingRunId: uuid("training_run_id").references(() => trainingRuns.id, {
      onDelete: "set null",
    }),
    name: text("name").notNull(),
    version: text("version").notNull(),
    architecture: text("architecture").notNull(),
    licence: text("licence").notNull(),
    stage: text("stage")
      .notNull()
      .$type<"candidate" | "shadow" | "production" | "archived">()
      .default("candidate"),
    metrics: jsonb("metrics").notNull().default({}),
    artifactKey: text("artifact_key").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("models_org_stage_idx").on(t.orgId, t.stage)],
);

export const apiKeys = pgTable(
  "api_keys",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    keyPrefix: text("key_prefix").notNull(),
    keyHash: text("key_hash").notNull().unique(),
    role: text("role").notNull().$type<"owner" | "admin" | "member" | "viewer">(),
    lastUsedAt: timestamp("last_used_at", { withTimezone: true }),
    revokedAt: timestamp("revoked_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("api_keys_org_idx").on(t.orgId)],
);

export const auditLogs = pgTable(
  "audit_logs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    orgId: uuid("org_id")
      .notNull()
      .references(() => orgs.id, { onDelete: "cascade" }),
    actorUserId: uuid("actor_user_id"),
    action: text("action").notNull(),
    resourceType: text("resource_type").notNull(),
    resourceId: text("resource_id").notNull(),
    metadata: jsonb("metadata").notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => [index("audit_logs_org_created_idx").on(t.orgId, t.createdAt)],
);

/**
 * Idempotent DDL migration runner that creates all 13 core tables, converts
 * `frame_events` into a TimescaleDB hypertable partitioned by `observed_at`,
 * and configures columnar compression on historical chunks.
 */
export async function runMigrations(sql: postgres.Sql): Promise<void> {
  await sql`CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE`;
  await sql`CREATE EXTENSION IF NOT EXISTS pgcrypto`;

  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      email text NOT NULL UNIQUE,
      name text NOT NULL,
      password_hash text NOT NULL,
      password_salt text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS orgs (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      name text NOT NULL,
      slug text NOT NULL UNIQUE,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS org_members (
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      role text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (org_id, user_id)
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS sessions (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      token_hash text NOT NULL UNIQUE,
      user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      expires_at timestamptz NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS projects (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      name text NOT NULL,
      description text NOT NULL DEFAULT '',
      privacy_mode boolean NOT NULL DEFAULT true,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS projects_org_idx ON projects (org_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS media (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      kind text NOT NULL,
      filename text NOT NULL,
      mime_type text NOT NULL,
      size_bytes bigint NOT NULL,
      storage_key text NOT NULL,
      status text NOT NULL DEFAULT 'uploading',
      width integer,
      height integer,
      duration_seconds double precision,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS media_org_project_idx ON media (org_id, project_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS analyses (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      media_id uuid NOT NULL REFERENCES media(id) ON DELETE CASCADE,
      status text NOT NULL DEFAULT 'queued',
      idempotency_key text NOT NULL,
      config jsonb NOT NULL DEFAULT '{}'::jsonb,
      summary jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now(),
      completed_at timestamptz,
      UNIQUE (org_id, idempotency_key)
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS analyses_org_media_idx ON analyses (org_id, media_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS frame_events (
      observed_at timestamptz NOT NULL,
      org_id uuid NOT NULL,
      analysis_id uuid NOT NULL,
      frame_index integer NOT NULL,
      people_count integer NOT NULL,
      unique_track_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
      detections jsonb NOT NULL DEFAULT '[]'::jsonb,
      zone_counts jsonb NOT NULL DEFAULT '{}'::jsonb,
      PRIMARY KEY (org_id, analysis_id, frame_index, observed_at)
    )
  `;
  await sql`SELECT create_hypertable('frame_events', by_range('observed_at', INTERVAL '1 day'), if_not_exists => TRUE)`;
  await sql`CREATE INDEX IF NOT EXISTS frame_events_org_time_idx ON frame_events (org_id, observed_at DESC)`;

  await sql`
    CREATE TABLE IF NOT EXISTS tracks (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL,
      analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
      track_number integer NOT NULL,
      label text NOT NULL,
      first_frame integer NOT NULL,
      last_frame integer NOT NULL,
      avg_confidence double precision NOT NULL,
      dominant_colours jsonb NOT NULL DEFAULT '[]'::jsonb,
      upper_clothing_colours jsonb NOT NULL DEFAULT '[]'::jsonb,
      lower_clothing_colours jsonb NOT NULL DEFAULT '[]'::jsonb,
      trajectory jsonb NOT NULL DEFAULT '[]'::jsonb
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS tracks_org_analysis_idx ON tracks (org_id, analysis_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS zones (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      name text NOT NULL,
      kind text NOT NULL,
      points jsonb NOT NULL,
      colour_hex text NOT NULL DEFAULT '#ffb21f',
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS zones_org_project_idx ON zones (org_id, project_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS alerts (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      name text NOT NULL,
      rule_type text NOT NULL,
      condition jsonb NOT NULL,
      channels jsonb NOT NULL DEFAULT '[]'::jsonb,
      enabled boolean NOT NULL DEFAULT true,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS alerts_org_project_idx ON alerts (org_id, project_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS datasets (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      name text NOT NULL,
      format text NOT NULL,
      classes jsonb NOT NULL DEFAULT '[]'::jsonb,
      item_count integer NOT NULL DEFAULT 0,
      health_report jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS datasets_org_idx ON datasets (org_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS annotations (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL,
      dataset_id uuid NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
      media_id uuid NOT NULL REFERENCES media(id) ON DELETE CASCADE,
      frame_index integer NOT NULL DEFAULT 0,
      boxes jsonb NOT NULL DEFAULT '[]'::jsonb,
      source text NOT NULL,
      reviewed boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS annotations_org_dataset_idx ON annotations (org_id, dataset_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS training_runs (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      dataset_id uuid NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
      base_architecture text NOT NULL,
      preset text NOT NULL,
      status text NOT NULL DEFAULT 'queued',
      hyperparams jsonb NOT NULL DEFAULT '{}'::jsonb,
      metrics_history jsonb NOT NULL DEFAULT '[]'::jsonb,
      final_metrics jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS training_runs_org_idx ON training_runs (org_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS models (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      training_run_id uuid REFERENCES training_runs(id) ON DELETE SET NULL,
      name text NOT NULL,
      version text NOT NULL,
      architecture text NOT NULL,
      licence text NOT NULL,
      stage text NOT NULL DEFAULT 'candidate',
      metrics jsonb NOT NULL DEFAULT '{}'::jsonb,
      artifact_key text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS models_org_stage_idx ON models (org_id, stage)`;

  await sql`
    CREATE TABLE IF NOT EXISTS api_keys (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      name text NOT NULL,
      key_prefix text NOT NULL,
      key_hash text NOT NULL UNIQUE,
      role text NOT NULL,
      last_used_at timestamptz,
      revoked_at timestamptz,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS api_keys_org_idx ON api_keys (org_id)`;

  await sql`
    CREATE TABLE IF NOT EXISTS audit_logs (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
      actor_user_id uuid,
      action text NOT NULL,
      resource_type text NOT NULL,
      resource_id text NOT NULL,
      metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS audit_logs_org_created_idx ON audit_logs (org_id, created_at DESC)`;
}
