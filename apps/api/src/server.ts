import Fastify from "fastify";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";
import postgres from "postgres";
import { Redis } from "ioredis";
import { loadEnv } from "./env.ts";
import { probe } from "./health.ts";

const env = loadEnv();
const app = Fastify({
  logger: { level: env.NODE_ENV === "production" ? "info" : "debug", redact: ["req.headers.authorization", "req.headers.cookie"] },
});
const sql = postgres(env.DATABASE_URL, { max: 10, idle_timeout: 20 });
const redis = new Redis(env.REDIS_URL, { lazyConnect: true, maxRetriesPerRequest: 1 });

await app.register(helmet);
await app.register(cors, { origin: env.CORS_ORIGINS.split(","), credentials: true });

app.get("/healthz", async () => ({ status: "ok" }));

app.get("/readyz", async (_req, reply) => {
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
});

const shutdown = async (sig: string) => {
  app.log.info({ sig }, "shutting down");
  await app.close();
  await Promise.allSettled([sql.end({ timeout: 5 }), redis.quit()]);
  process.exit(0);
};
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

await app.listen({ port: env.PORT, host: "0.0.0.0" });
