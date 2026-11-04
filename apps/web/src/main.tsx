import { StrictMode, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Button,
  type ButtonStatus,
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
import { CanvasOverlay, type DetectionItem } from "./components/CanvasOverlay";
import "./app.css";

interface AuthSession {
  token: string;
  user: { id: string; email: string; name: string };
  org: { id: string; name: string; slug: string; role: string };
}

interface ProjectRow {
  id: string;
  name: string;
  description: string;
  privacyMode: boolean;
  createdAt: string;
}

interface ApiKeyRow {
  id: string;
  name: string;
  keyPrefix: string;
  role: string;
  secretKey?: string;
}

interface SampleItem {
  id: string;
  title: string;
  dataUrl: string;
}

interface FrameAnalysisResult {
  width: number;
  height: number;
  preset: string;
  architecture: string;
  latencyMs: number;
  peopleCount: number;
  uncertainCount: number;
  detections: DetectionItem[];
  frameIndex: number;
}

interface BenchmarkReport {
  evaluatedAt: string;
  hardware: {
    machine: string;
    python: string;
    onnxruntime: string;
    providers: string[];
  };
  models: {
    balanced: {
      name: string;
      licence: string;
      sizeMb: number;
      latencyP50Ms: number;
      latencyP95Ms: number;
      fpsP50: number;
    };
    fast: {
      name: string;
      licence: string;
      sizeMb: number;
      latencyP50Ms: number;
      latencyP95Ms: number;
      fpsP50: number;
    };
  };
  metrics: {
    mAP50: number;
    mAP50_95: number;
    personCountMAE: number;
    personExactMatchRate: number;
    colourNamingAccuracy: number;
    trackIdSwitchesPerMin: number;
    trackIdentityPreservation: number;
  };
}

function App() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [ready, setReady] = useState<ReadyResponse | null>(null);
  const [probing, setProbing] = useState(false);

  const [session, setSession] = useState<AuthSession | null>(() => {
    const saved = localStorage.getItem("vl_session");
    return saved ? (JSON.parse(saved) as AuthSession) : null;
  });

  // Auth form state
  const [authMode, setAuthMode] = useState<"register" | "login">("register");
  const [email, setEmail] = useState("lead@visionlytics.io");
  const [password, setPassword] = useState("optics-bench-2026");
  const [name, setName] = useState("Dr. Maya Lin");
  const [orgName, setOrgName] = useState("Meridian Optics");
  const [orgSlug, setOrgSlug] = useState("meridian-optics");
  const [authError, setAuthError] = useState<string | undefined>();
  const [authStatus, setAuthStatus] = useState<ButtonStatus>("idle");

  // Workspace state
  const [projects, setProjects] = useState<ProjectRow[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKeyRow[]>([]);
  const [newProjectName, setNewProjectName] = useState("North Terminal Gate 4");
  const [newKeyName, setNewKeyName] = useState("Edge Ingest Worker");
  const [latestSecretKey, setLatestSecretKey] = useState<string | null>(null);

  // Phase 3/4: Analyze & Results Viewer state
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkReport | null>(null);
  const [activeImageUrl, setActiveImageUrl] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<FrameAnalysisResult | null>(null);
  const [frameHistory, setFrameHistory] = useState<FrameAnalysisResult[]>([]);
  const [scrubIndex, setScrubIndex] = useState<number>(0);
  const [inferStatus, setInferStatus] = useState<ButtonStatus>("idle");
  const [preset, setPreset] = useState<"fast" | "balanced" | "max_accuracy">("balanced");
  const [threshold, setThreshold] = useState(0.5);
  const [privacyMode, setPrivacyMode] = useState(true);
  const [tiledMode, setTiledMode] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [openVocabQuery, setOpenVocabQuery] = useState("");
  const [highlightedTrackId, setHighlightedTrackId] = useState<number | null>(null);

  const webcamVideoRef = useRef<HTMLVideoElement | null>(null);
  const [webcamActive, setWebcamActive] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const runProbe = async () => {
    setProbing(true);
    try {
      const [readyRes, benchRes, sampRes] = await Promise.all([
        fetch("/api/readyz"),
        fetch("/api/v1/ml/benchmarks"),
        fetch("/api/v1/ml/samples"),
      ]);
      if (readyRes.ok) setReady((await readyRes.json()) as ReadyResponse);
      if (benchRes.ok) setBenchmarks((await benchRes.json()) as BenchmarkReport);
      if (sampRes.ok) {
        const sData = (await sampRes.json()) as { items: SampleItem[] };
        setSamples(sData.items);
        if (sData.items[0] && !activeImageUrl) {
          setActiveImageUrl(sData.items[0].dataUrl);
        }
      }
    } catch {
      setReady(null);
    } finally {
      setProbing(false);
    }
  };

  const loadWorkspace = async (tok: string) => {
    const [pRes, kRes] = await Promise.all([
      fetch("/api/v1/projects", { headers: { authorization: `Bearer ${tok}` } }),
      fetch("/api/v1/api-keys", { headers: { authorization: `Bearer ${tok}` } }),
    ]);
    if (pRes.ok) {
      const pData = (await pRes.json()) as { items: ProjectRow[] };
      setProjects(pData.items);
    }
    if (kRes.ok) {
      const kData = (await kRes.json()) as { items: ApiKeyRow[] };
      setApiKeys(kData.items);
    }
  };

  useEffect(() => {
    void runProbe();
  }, []);

  useEffect(() => {
    if (session) {
      void loadWorkspace(session.token);
    }
  }, [session]);

  const handleAuth = async () => {
    setAuthError(undefined);
    setAuthStatus("loading");
    try {
      const url = authMode === "register" ? "/api/v1/auth/register" : "/api/v1/auth/login";
      const body =
        authMode === "register"
          ? { email, password, name, orgName, orgSlug }
          : { email, password };
      const r = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = (await r.json()) as AuthSession & { error?: string };
      if (!r.ok) {
        setAuthError(data.error ?? "Authentication failed");
        setAuthStatus("error");
        return;
      }
      localStorage.setItem("vl_session", JSON.stringify(data));
      setSession(data);
      setAuthStatus("success");
    } catch (e) {
      setAuthError((e as Error).message);
      setAuthStatus("error");
    }
  };

  const runFrameInference = async (dataUrlToAnalyze?: string) => {
    const imgUrl = dataUrlToAnalyze ?? activeImageUrl;
    if (!session || !imgUrl) return;
    setInferStatus("loading");
    try {
      const nextFrameIdx = frameHistory.length;
      const r = await fetch("/api/v1/ml/infer-frame", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          projectId: projects[0]?.id,
          imageBase64: imgUrl,
          preset,
          minConfidence: 0.28,
          uncertainThreshold: threshold,
          tiled: tiledMode,
          openVocabQuery: openVocabQuery.trim() || undefined,
          streamId: "workspace-live-stream",
          frameIndex: nextFrameIdx,
        }),
      });
      if (!r.ok) {
        setInferStatus("error");
        return;
      }
      const res = (await r.json()) as FrameAnalysisResult;
      setAnalysisResult(res);
      setFrameHistory((prev) => {
        const updated = [...prev, res];
        setScrubIndex(updated.length - 1);
        return updated;
      });
      setInferStatus("success");
      setTimeout(() => setInferStatus("idle"), 900);
    } catch {
      setInferStatus("error");
    }
  };

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        setActiveImageUrl(reader.result);
        void runFrameInference(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  const toggleWebcam = async () => {
    if (webcamActive) {
      const stream = webcamVideoRef.current?.srcObject as MediaStream | null;
      stream?.getTracks().forEach((t) => t.stop());
      setWebcamActive(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 540 } });
      if (webcamVideoRef.current) {
        webcamVideoRef.current.srcObject = stream;
        await webcamVideoRef.current.play();
        setWebcamActive(true);
      }
    } catch {
      setWebcamActive(false);
    }
  };

  const captureWebcamFrame = () => {
    const v = webcamVideoRef.current;
    if (!v) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth || 640;
    c.height = v.videoHeight || 480;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(v, 0, 0, c.width, c.height);
    const dataUrl = c.toDataURL("image/jpeg", 0.9);
    setActiveImageUrl(dataUrl);
    void runFrameInference(dataUrl);
  };

  const createProject = async () => {
    if (!session || !newProjectName.trim()) return;
    const r = await fetch("/api/v1/projects", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${session.token}`,
      },
      body: JSON.stringify({
        name: newProjectName,
        description: "Live camera and batch video telemetry project",
        privacyMode,
      }),
    });
    if (r.ok) {
      setNewProjectName("");
      await loadWorkspace(session.token);
    }
  };

  const createApiKey = async () => {
    if (!session || !newKeyName.trim()) return;
    const r = await fetch("/api/v1/api-keys", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${session.token}`,
      },
      body: JSON.stringify({ name: newKeyName, role: "member" }),
    });
    if (r.ok) {
      const created = (await r.json()) as ApiKeyRow;
      setLatestSecretKey(created.secretKey ?? null);
      setNewKeyName("");
      await loadWorkspace(session.token);
    }
  };

  const healthyCount = ready ? ready.checks.filter((c) => c.ok).length : 0;
  const activeFrame = frameHistory[scrubIndex] ?? analysisResult;

  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="border-b border-hairline bg-surface/70">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div className="flex items-baseline gap-3">
            <span className="font-display text-xl font-bold tracking-tight">Visionlytics</span>
            <span className="tabular text-xs text-muted">v0.4.0</span>
            {session && (
              <span className="tabular rounded-[var(--radius-hair)] border border-hairline-strong px-2 py-0.5 text-2xs text-signal">
                {session.org.slug} · {session.org.role}
              </span>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <a
              href="/api/docs"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 text-sm text-muted hover:text-fg"
            >
              OpenAPI 3.1
            </a>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            >
              {theme === "dark" ? "Bench lamp (light)" : "Night optics (dark)"}
            </Button>
            <Button
              size="sm"
              variant="secondary"
              status={probing ? "loading" : "idle"}
              loadingLabel="Probing dependencies"
              onClick={runProbe}
            >
              Probe services
            </Button>
            {session && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  localStorage.removeItem("vl_session");
                  setSession(null);
                  setProjects([]);
                  setApiKeys([]);
                }}
              >
                Sign out
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8">
        {/* Top Row: Auth / Analyze Workspace + Calibration Sidebar */}
        <div className="grid gap-6 lg:grid-cols-[1.65fr_1fr]">
          <Panel
            title={
              session
                ? "Analyze workspace & 60fps canvas overlay"
                : "Operator onboarding & authentication"
            }
            meta={
              session ? (
                <span className="tabular text-xs text-muted">
                  {activeFrame
                    ? `${activeFrame.architecture} · ${activeFrame.latencyMs}ms · ${activeFrame.width}×${activeFrame.height}`
                    : "Select a golden scene or upload media"}
                </span>
              ) : (
                "RBAC + tenant isolation"
              )
            }
          >
            {!session ? (
              <div className="grid gap-4">
                <div className="flex gap-2">
                  <Button
                    variant={authMode === "register" ? "primary" : "secondary"}
                    size="sm"
                    onClick={() => setAuthMode("register")}
                  >
                    New organization
                  </Button>
                  <Button
                    variant={authMode === "login" ? "primary" : "secondary"}
                    size="sm"
                    onClick={() => setAuthMode("login")}
                  >
                    Sign in
                  </Button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Field
                    label="Work email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <Field
                    label="Passphrase"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  {authMode === "register" && (
                    <>
                      <Field
                        label="Operator name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                      <Field
                        label="Organization name"
                        value={orgName}
                        onChange={(e) => setOrgName(e.target.value)}
                      />
                      <Field
                        label="Tenant slug"
                        value={orgSlug}
                        onChange={(e) => setOrgSlug(e.target.value)}
                        error={authError}
                      />
                    </>
                  )}
                </div>
                <div>
                  <Button status={authStatus} onClick={handleAuth}>
                    {authMode === "register" ? "Initialize workspace" : "Open workspace"}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid gap-5">
                {/* Input selector toolbar */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline pb-4">
                  <div className="flex flex-wrap items-center gap-2">
                    {samples.map((s) => (
                      <Button
                        key={s.id}
                        size="sm"
                        variant={activeImageUrl === s.dataUrl ? "primary" : "secondary"}
                        onClick={() => {
                          setActiveImageUrl(s.dataUrl);
                          void runFrameInference(s.dataUrl);
                        }}
                      >
                        {s.id === "bus_street.jpg" ? "Scene: Urban street" : "Scene: Close subjects"}
                      </Button>
                    ))}
                    <label className="inline-flex h-8 cursor-pointer items-center rounded-[var(--radius-key)] border border-hairline-strong bg-raised px-3 text-sm text-fg hover:border-fg/50">
                      Upload image/frame
                      <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        className="sr-only"
                        onChange={(e) => {
                          const f = e.target.files?.[0];
                          if (f) handleFileUpload(f);
                        }}
                      />
                    </label>
                    <Button size="sm" variant="secondary" onClick={toggleWebcam}>
                      {webcamActive ? "Stop webcam" : "Live webcam"}
                    </Button>
                    {webcamActive && (
                      <Button size="sm" onClick={captureWebcamFrame}>
                        Capture & infer
                      </Button>
                    )}
                  </div>
                  <Button
                    size="sm"
                    status={inferStatus}
                    loadingLabel="Running ONNX"
                    onClick={() => void runFrameInference()}
                  >
                    Run inference
                  </Button>
                </div>

                {webcamActive && (
                  <video
                    ref={webcamVideoRef}
                    muted
                    playsInline
                    className="max-h-48 w-full border border-signal bg-bg object-contain"
                  />
                )}

                {/* Annotated Canvas Overlay */}
                <CanvasOverlay
                  imageDataUrl={activeImageUrl}
                  naturalWidth={activeFrame?.width ?? 810}
                  naturalHeight={activeFrame?.height ?? 1080}
                  detections={activeFrame?.detections ?? []}
                  showHeatmap={showHeatmap}
                  privacyBlur={privacyMode}
                  highlightedTrackId={highlightedTrackId}
                />

                {/* Synced timeline scrubber & live counters */}
                <div className="grid gap-4 border-t border-hairline pt-4 sm:grid-cols-[1fr_1.4fr]">
                  <div className="flex flex-wrap items-end gap-8">
                    <Readout
                      value={activeFrame?.peopleCount ?? 0}
                      label="People in frame"
                      size="xl"
                    />
                    <Readout
                      value={activeFrame?.detections.length ?? 0}
                      label="Objects tracked"
                      unit="ids"
                    />
                  </div>
                  <div className="grid gap-2">
                    <div className="flex items-center justify-between text-xs text-muted">
                      <span>Timeline scrubber ({frameHistory.length} frames persisted to TimescaleDB)</span>
                      <span className="tabular">
                        Frame #{activeFrame?.frameIndex ?? 0} · {activeFrame?.latencyMs ?? 0}ms
                      </span>
                    </div>
                    <input
                      type="range"
                      aria-label="Timeline frame scrubber"
                      min={0}
                      max={Math.max(0, frameHistory.length - 1)}
                      value={scrubIndex}
                      onChange={(e) => setScrubIndex(Number(e.target.value))}
                      className="w-full accent-[var(--vl-signal)]"
                    />
                  </div>
                </div>
              </div>
            )}
          </Panel>

          {/* Calibration & Open-Vocab Sidebar */}
          <div className="grid content-start gap-6">
            <Panel title="Calibration & inference controls" meta="Live parameters">
              <div className="grid gap-5">
                <div className="grid gap-1.5">
                  <span className="text-sm text-muted">Model preset (Apache-2.0)</span>
                  <div className="flex gap-2">
                    {(["fast", "balanced", "max_accuracy"] as const).map((p) => (
                      <Button
                        key={p}
                        size="sm"
                        variant={preset === p ? "primary" : "secondary"}
                        onClick={() => setPreset(p)}
                      >
                        {p === "fast" ? "Fast (YOLOS)" : p === "balanced" ? "Balanced (RT-DETRv2)" : "Max accuracy"}
                      </Button>
                    ))}
                  </div>
                </div>
                <Field
                  label="Open-vocabulary & colour search"
                  placeholder="e.g. person, bus, navy, beige"
                  value={openVocabQuery}
                  onChange={(e) => setOpenVocabQuery(e.target.value)}
                  hint="Filters frame detections by object class or CIELAB colour name"
                />
                <Slider
                  label="Uncertain confidence threshold"
                  value={threshold}
                  onValueChange={setThreshold}
                />
                <Switch
                  label="Privacy redaction"
                  description="Blur faces on canvas before export or storage"
                  checked={privacyMode}
                  onCheckedChange={setPrivacyMode}
                />
                <Switch
                  label="Crowd density heatmap"
                  description="Overlay radial person-density field on the viewport"
                  checked={showHeatmap}
                  onCheckedChange={setShowHeatmap}
                />
                <Switch
                  label="Small-object tiled mode (SAHI)"
                  description="Run 2×2 overlapping tiles for distant objects"
                  checked={tiledMode}
                  onCheckedChange={setTiledMode}
                />
              </div>
            </Panel>

            <Panel
              title="Infrastructure telemetry"
              meta={ready ? `Status: ${ready.status}` : "Awaiting probe"}
            >
              <div className="flex flex-wrap items-end gap-8">
                <Readout value={healthyCount} label="Services online" size="lg" />
                <Readout
                  value={ready ? ready.checks.length : 0}
                  label="Total checks"
                  unit="nodes"
                  size="md"
                />
              </div>
              {ready && (
                <ul className="mt-4 grid gap-1.5 border-t border-hairline pt-3 text-xs">
                  {ready.checks.map((c) => (
                    <li key={c.name} className="flex items-center justify-between">
                      <span className="text-fg">{c.name}</span>
                      <span className="tabular text-muted">
                        {c.ok ? `ok · ${c.latencyMs}ms` : `error · ${c.error ?? "unreachable"}`}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Panel>
          </div>
        </div>

        {/* Second Row: Per-Object Results Table (with Clothing Colours) + Real Evaluation Benchmarks */}
        <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <Panel
            title="Detected objects & CIELAB colour breakdown"
            meta={`${activeFrame?.detections.length ?? 0} objects in current frame`}
          >
            {activeFrame && activeFrame.detections.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-hairline text-xs text-muted">
                      <th className="py-2 pr-3 font-normal">Track ID</th>
                      <th className="py-2 pr-3 font-normal">Class</th>
                      <th className="py-2 pr-3 font-normal">Confidence</th>
                      <th className="py-2 pr-3 font-normal">Dominant colours (foreground mask)</th>
                      <th className="py-2 font-normal">Attire (upper / lower)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeFrame.detections.map((d) => (
                      <tr
                        key={d.trackId}
                        onMouseEnter={() => setHighlightedTrackId(d.trackId)}
                        onMouseLeave={() => setHighlightedTrackId(null)}
                        className="border-b border-hairline/60 hover:bg-raised/60"
                      >
                        <td className="tabular py-2.5 pr-3 text-signal">#{d.trackId}</td>
                        <td className="py-2.5 pr-3 font-medium text-fg">{d.label}</td>
                        <td className="py-2.5 pr-3">
                          <Confidence score={d.confidence} threshold={threshold} />
                        </td>
                        <td className="py-2.5 pr-3">
                          <div className="flex flex-wrap gap-3">
                            {d.colours.map((c) => (
                              <ColourChip
                                key={c.name}
                                name={c.name}
                                hex={c.hex}
                                share={c.share}
                              />
                            ))}
                          </div>
                        </td>
                        <td className="py-2.5 text-xs text-muted">
                          {d.upperClothingColours?.[0] && d.lowerClothingColours?.[0] ? (
                            <div className="flex flex-wrap gap-2">
                              <ColourChip
                                name={`Top: ${d.upperClothingColours[0].name}`}
                                hex={d.upperClothingColours[0].hex}
                              />
                              <ColourChip
                                name={`Bottom: ${d.lowerClothingColours[0].name}`}
                                hex={d.lowerClothingColours[0].hex}
                              />
                            </div>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-muted">
                Sign in and click &ldquo;Scene: Urban street&rdquo; or &ldquo;Run inference&rdquo; to inspect per-object bounding boxes, track IDs, and foreground CIELAB colour percentages.
              </p>
            )}
          </Panel>

          <Panel
            title="Measured ML evaluation harness"
            meta={benchmarks ? `Hardware: ${benchmarks.hardware.machine} · ORT ${benchmarks.hardware.onnxruntime}` : "Loading metrics"}
          >
            {benchmarks ? (
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4 border-b border-hairline pb-4">
                  <Readout
                    value={Math.round(benchmarks.metrics.mAP50 * 100)}
                    label="Golden set mAP50"
                    unit="%"
                    size="md"
                  />
                  <Readout
                    value={Math.round(benchmarks.metrics.mAP50_95 * 100)}
                    label="Golden set mAP50-95"
                    unit="%"
                    size="md"
                  />
                  <Readout
                    value={Math.round(benchmarks.metrics.colourNamingAccuracy * 100)}
                    label="CIEDE2000 colour accuracy"
                    unit="%"
                    size="md"
                  />
                  <Readout
                    value={Math.round(benchmarks.metrics.personExactMatchRate * 100)}
                    label="Person count exact match"
                    unit="%"
                    size="md"
                  />
                </div>
                <dl className="grid gap-1.5 text-xs">
                  <div className="flex justify-between">
                    <dt className="text-muted">Balanced detector ({benchmarks.models.balanced.name})</dt>
                    <dd className="tabular text-fg">
                      p50 {benchmarks.models.balanced.latencyP50Ms}ms · p95 {benchmarks.models.balanced.latencyP95Ms}ms ({benchmarks.models.balanced.licence})
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted">Fast detector ({benchmarks.models.fast.name})</dt>
                    <dd className="tabular text-fg">
                      p50 {benchmarks.models.fast.latencyP50Ms}ms · p95 {benchmarks.models.fast.latencyP95Ms}ms ({benchmarks.models.fast.licence})
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted">Tracker ID switches / min (occlusion test)</dt>
                    <dd className="tabular text-fg">{benchmarks.metrics.trackIdSwitchesPerMin}</dd>
                  </div>
                </dl>
              </div>
            ) : (
              <p className="text-sm text-muted">Fetching real evaluation harness report…</p>
            )}
          </Panel>
        </div>

        {/* Third Row: Organization Projects & API Keys */}
        {session && (
          <Panel
            title={`Organization management — ${session.org.name}`}
            meta={
              <span className="inline-block max-w-[220px] truncate align-bottom" title={session.user.email}>
                {session.user.email}
              </span>
            }
          >
            <Tabs defaultValue="projects">
              <TabsList label="Workspace sections">
                <TabsTrigger value="projects" count={projects.length}>
                  Projects
                </TabsTrigger>
                <TabsTrigger value="apikeys" count={apiKeys.length}>
                  API keys
                </TabsTrigger>
              </TabsList>
              <TabsContent value="projects">
                <div className="grid gap-4">
                  <div className="flex flex-wrap items-end gap-3">
                    <Field
                      label="New project name"
                      value={newProjectName}
                      onChange={(e) => setNewProjectName(e.target.value)}
                      className="grow"
                    />
                    <Button size="md" onClick={createProject}>
                      Create project
                    </Button>
                  </div>
                  <ul className="grid gap-2 text-sm sm:grid-cols-2">
                    {projects.map((p) => (
                      <li
                        key={p.id}
                        className="flex items-center justify-between border border-hairline bg-bg/60 px-3 py-2"
                      >
                        <div>
                          <div className="font-medium text-fg">{p.name}</div>
                          <div className="text-xs text-muted">{p.description}</div>
                        </div>
                        <span className="tabular text-2xs text-muted">
                          {p.privacyMode ? "privacy blur: on" : "privacy blur: off"}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
              <TabsContent value="apikeys">
                <div className="grid gap-4">
                  <div className="flex flex-wrap items-end gap-3">
                    <Field
                      label="Key label"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="grow"
                    />
                    <Button size="md" onClick={createApiKey}>
                      Generate key
                    </Button>
                  </div>
                  {latestSecretKey && (
                    <div className="border border-signal/60 bg-signal-wash p-3 text-xs">
                      <div className="text-muted">Copy secret key now (stored hashed with SHA-256):</div>
                      <code className="tabular mt-1 block text-fg">{latestSecretKey}</code>
                    </div>
                  )}
                  <ul className="grid gap-2 text-sm sm:grid-cols-2">
                    {apiKeys.map((k) => (
                      <li
                        key={k.id}
                        className="flex items-center justify-between border border-hairline bg-bg/60 px-3 py-2"
                      >
                        <span className="text-fg">{k.name}</span>
                        <span className="tabular text-xs text-muted">
                          {k.keyPrefix}… · {k.role}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
            </Tabs>
          </Panel>
        )}
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
