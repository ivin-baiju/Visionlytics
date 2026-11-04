import { StrictMode, useEffect, useState } from "react";
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

  // Calibration controls
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

  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="border-b border-hairline bg-surface/70">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div className="flex items-baseline gap-3">
            <span className="font-display text-xl font-bold tracking-tight">Visionlytics</span>
            <span className="tabular text-xs text-muted">v0.2.0</span>
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

      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-8 md:grid-cols-[1.35fr_1fr]">
        <Panel
          title={session ? `Organization workspace — ${session.org.name}` : "Operator onboarding & authentication"}
          meta={
            session ? (
              <span className="inline-block max-w-[200px] truncate align-bottom" title={session.user.email}>
                {session.user.email}
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
                  <ul className="grid gap-2 text-sm">
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
                  <ul className="grid gap-2 text-sm">
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
          )}
        </Panel>

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
              <p className="text-sm text-muted">Probing backing services…</p>
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

        <Panel title="Optical primitives">
          <div className="grid gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <Confidence score={0.88} threshold={threshold} />
              <Confidence score={0.41} threshold={threshold} />
            </div>
            <div className="flex flex-wrap gap-4">
              <ColourChip name="Signal Amber" hex="#ffb21f" share={0.54} />
              <ColourChip name="Charcoal" hex="#23272b" share={0.31} />
              <ColourChip name="Warm Chalk" hex="#ede8de" share={0.15} />
            </div>
          </div>
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
