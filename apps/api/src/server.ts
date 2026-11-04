import { loadEnv } from "./env.ts";
import { buildApp } from "./app.ts";

const env = loadEnv();
const runtime = await buildApp(env);

const shutdown = async (sig: string) => {
  runtime.app.log.info({ sig }, "shutting down");
  await runtime.close();
  process.exit(0);
};
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

await runtime.app.listen({ port: env.PORT, host: "0.0.0.0" });
