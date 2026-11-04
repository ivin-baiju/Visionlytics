import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Button,
  ColourChip,
  Confidence,
  Field,
  Panel,
  Readout,
  Slider,
  Switch,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@visionlytics/ui";
import type { ReadyResponse } from "@visionlytics/shared-types";
import "./app.css";

function App() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [ready, setReady] = useState<ReadyResponse | null>(null);
  const [probing, setProbing] = useState(false);
  const [threshold, setThreshold] = useState(0.5);
  const [privacyMode, setPrivacyMode] = useState(true);
  const [tiledMode, setTiledMode] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const runProbe = async () => {
    setProbing(true);
    try {
      const r = await fetch("/api/readyz");
      const data = (await r.json()) as ReadyResponse;
      setReady(data);
    } catch {
      setReady(null);
    } finally {
      setProbing(false);
    }
  };

  useEffect(() => {
    void runProbe();
  }, []);

  const healthyCount = ready ? ready.checks.filter((c) => c.ok).length : 0;

  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="border-b border-hairline bg-surface/70">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div className="flex items-baseline gap-3">
            <span className="font-display text-xl font-bold tracking-tight">Visionlytics</span>
            <span className="tabular text-xs text-muted">v0.1.0</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            >
              {theme === "dark" ? "Bench lamp (light)" : "Night optics (dark)"}
            </Button>
            <Button
              size="sm"
              status={probing ? "loading" : "idle"}
              loadingLabel="Probing dependencies"
              onClick={runProbe}
            >
              Probe services
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-8 md:grid-cols-[1.35fr_1fr]">
        <Panel
          title="Infrastructure telemetry"
          meta={ready ? `Status: ${ready.status}` : "Awaiting probe"}
        >
          <div className="flex flex-wrap items-end gap-10">
            <Readout value={healthyCount} label="Services online" size="xl" />
            <Readout
              value={ready ? ready.checks.length : 0}
              label="Total checks"
              unit="nodes"
            />
          </div>
          <div className="mt-6 border-t border-hairline pt-4">
            {ready ? (
              <ul className="grid gap-2 text-sm">
                {ready.checks.map((c) => (
                  <li
                    key={c.name}
                    className="flex items-center justify-between border-b border-hairline/60 py-1.5 last:border-none"
                  >
                    <span className="text-fg">{c.name}</span>
                    <span className="tabular text-xs text-muted">
                      {c.ok ? `ok · ${c.latencyMs}ms` : `error · ${c.error ?? "unreachable"}`}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">
                Backend readiness probe not yet connected. Start the stack with docker compose to inspect live service latencies.
              </p>
            )}
          </div>
        </Panel>

        <Panel title="Calibration controls" meta="Session defaults">
          <div className="grid gap-5">
            <Slider
              label="Confidence threshold"
              value={threshold}
              onValueChange={setThreshold}
            />
            <Switch
              label="Privacy redaction"
              description="Blur faces and registration plates before frame persistence"
              checked={privacyMode}
              onCheckedChange={setPrivacyMode}
            />
            <Switch
              label="Tiled small-object pass"
              description="Run SAHI overlapping crops for high-altitude or wide-angle feeds"
              checked={tiledMode}
              onCheckedChange={setTiledMode}
            />
          </div>
        </Panel>

        <Panel title="Design system primitives">
          <Tabs defaultValue="confidence">
            <TabsList label="Primitive groups">
              <TabsTrigger value="confidence">Confidence state</TabsTrigger>
              <TabsTrigger value="colours">CIELAB swatches</TabsTrigger>
              <TabsTrigger value="inputs">Stream input</TabsTrigger>
            </TabsList>
            <TabsContent value="confidence">
              <div className="flex flex-wrap items-center gap-3">
                <Confidence score={0.88} threshold={threshold} />
                <Confidence score={0.41} threshold={threshold} />
              </div>
            </TabsContent>
            <TabsContent value="colours">
              <div className="flex flex-wrap gap-4">
                <ColourChip name="Signal Amber" hex="#ffb21f" share={0.54} />
                <ColourChip name="Charcoal" hex="#23272b" share={0.31} />
                <ColourChip name="Warm Chalk" hex="#ede8de" share={0.15} />
              </div>
            </TabsContent>
            <TabsContent value="inputs">
              <Field
                label="RTSP camera endpoint"
                placeholder="rtsp://10.0.0.12:554/stream1"
                hint="Supports H.264/H.265 over TCP or UDP ingest"
              />
            </TabsContent>
          </Tabs>
        </Panel>
      </main>
    </div>
  );
}

const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
