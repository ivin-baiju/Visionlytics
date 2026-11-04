export type Check = { name: string; ok: boolean; latencyMs: number; error?: string };

/** Runs a dependency probe with a hard timeout so /readyz can never hang. */
export async function probe(name: string, fn: () => Promise<unknown>, timeoutMs = 1500): Promise<Check> {
  const t0 = performance.now();
  try {
    await Promise.race([
      fn(),
      new Promise((_, rej) => setTimeout(() => rej(new Error(`timeout after ${timeoutMs}ms`)), timeoutMs)),
    ]);
    return { name, ok: true, latencyMs: Math.round(performance.now() - t0) };
  } catch (e) {
    return { name, ok: false, latencyMs: Math.round(performance.now() - t0), error: (e as Error).message };
  }
}
