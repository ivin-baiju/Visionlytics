"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Database,
  Users,
  Activity,
  Trash2,
  RefreshCw,
  Search,
  ArrowLeft,
  Server,
  Image as ImageIcon,
  FileCheck2,
  LogOut,
} from "lucide-react";

interface AdminUser {
  id: number | string;
  username: string;
  email: string;
  phone?: string | null;
  role: string;
  is_verified?: boolean | number;
  created_at: string;
}

interface AdminAnalysis {
  id: number | string;
  source_type: string;
  people_count: number;
  density_label: string;
  occupancy_ratio: number;
  confidence: number;
  created_at?: string;
  timestamp?: string;
  features?: Record<string, unknown>;
}

interface AdminUpload {
  id: number | string;
  username: string;
  email: string;
  filename: string;
  file_size_bytes: number;
  content_type: string;
  thumbnail_base64?: string;
  people_count: number;
  density_label: string;
  confidence: number;
  created_at: string;
}

interface AdminConsentLog {
  id: number | string;
  consent_type: string;
  analytics_allowed: boolean | number;
  ip_hash: string;
  user_agent?: string;
  created_at: string;
}

export default function AdminPortalPage() {
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Tab
  const [activeTab, setActiveTab] = useState<"users" | "database" | "uploads" | "consent">("users");

  // Data states
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [analyses, setAnalyses] = useState<AdminAnalysis[]>([]);
  const [uploads, setUploads] = useState<AdminUpload[]>([]);
  const [consentLogs, setConsentLogs] = useState<AdminConsentLog[]>([]);
  const [overview, setOverview] = useState<{
    total_users: number;
    total_analyses: number;
    total_uploads: number;
    total_people_detected: number;
    database_engine: string;
  } | null>(null);

  // Search filter
  const [userSearch, setUserSearch] = useState("");
  const [analysisFilter, setAnalysisFilter] = useState("ALL");
  const [uploadSearch, setUploadSearch] = useState("");

  const loadAdminData = React.useCallback(async (authToken: string) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const headers = { Authorization: `Bearer ${authToken}` };

      const [ovRes, uRes, aRes, upRes, cRes] = await Promise.all([
        fetch("/api/py/admin/database/overview", { headers }),
        fetch("/api/py/admin/users", { headers }),
        fetch("/api/py/admin/database/analyses", { headers }),
        fetch("/api/py/admin/uploads", { headers }),
        fetch("/api/py/admin/consent-logs", { headers }),
      ]);

      if (ovRes.status === 401 || ovRes.status === 403) {
        setErrorMsg("Session expired or unauthorized. Please sign in with an Admin account.");
        setLoading(false);
        return;
      }

      if (!ovRes.ok || !uRes.ok) {
        throw new Error("Unable to fetch administrator database records. Backend may be unreachable.");
      }

      const parseJsonSafe = async (r: Response) => {
        const ct = r.headers.get("content-type") || "";
        return ct.includes("application/json") ? await r.json() : {};
      };

      const [ovData, uData, aData, upData, cData] = await Promise.all([
        parseJsonSafe(ovRes),
        parseJsonSafe(uRes),
        parseJsonSafe(aRes),
        parseJsonSafe(upRes),
        parseJsonSafe(cRes),
      ]);

      setOverview(ovData);
      setUsers(uData.users || []);
      setAnalyses(aData.analyses || []);
      setUploads(upData.uploads || []);
      setConsentLogs(cData.consent_logs || []);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to load database records.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Admin direct login form state
  const [adminIdentifier, setAdminIdentifier] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminLoginLoading, setAdminLoginLoading] = useState(false);

  const handleAdminLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdminLoginLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/py/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: adminIdentifier,
          password: adminPassword,
        }),
      });
      let data: any = {};
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        data = await res.json();
      } else {
        const text = await res.text();
        throw new Error(
          res.status === 404 || text.includes("page could not be found") || text.includes("DNS_HOSTNAME_RESOLVED_PRIVATE")
            ? "API backend service is unreachable from Vercel. Please ensure the backend is running and NEXT_PUBLIC_API_URL is configured."
            : text.slice(0, 120)
        );
      }
      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed.");
      }
      if (data.user?.role !== "admin") {
        throw new Error("Access Denied: This account does not possess administrator privileges.");
      }

      localStorage.setItem("visionlytics_token", data.access_token);
      localStorage.setItem("visionlytics_user", JSON.stringify(data.user));
      setToken(data.access_token);
      setCurrentUser(data.user);
      await loadAdminData(data.access_token);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to authenticate administrator.");
    } finally {
      setAdminLoginLoading(false);
    }
  };

  useEffect(() => {
    const frameId = requestAnimationFrame(() => {
      const savedToken = localStorage.getItem("visionlytics_token");
      const savedUserStr = localStorage.getItem("visionlytics_user");

      if (!savedToken) {
        setLoading(false);
        return;
      }

      try {
        const parsedUser = savedUserStr ? JSON.parse(savedUserStr) : null;
        if (parsedUser?.role !== "admin") {
          setErrorMsg("Access Denied: Your account does not have administrator privileges.");
          setLoading(false);
          return;
        }
        setToken(savedToken);
        setCurrentUser(parsedUser);
        loadAdminData(savedToken);
      } catch {
        setLoading(false);
      }
    });

    return () => cancelAnimationFrame(frameId);
  }, [loadAdminData]);

  const handleDeleteUser = async (userId: number | string) => {
    if (!token || !confirm("Are you sure you want to permanently delete this user?")) return;
    try {
      const res = await fetch(`/api/py/admin/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setUsers((prev) => prev.filter((u) => u.id !== userId));
      }
    } catch {
      alert("Failed to delete user.");
    }
  };

  const filteredUsers = users.filter((u) => {
    const q = userSearch.toLowerCase();
    return (
      u.username?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      (u.phone && u.phone.includes(q))
    );
  });

  const filteredAnalyses = analyses.filter((a) => {
    if (analysisFilter === "ALL") return true;
    return a.density_label === analysisFilter;
  });

  if (loading) {
    return (
      <div className="vl-container" style={{ textAlign: "center", paddingTop: "5rem" }}>
        <p style={{ color: "var(--text-secondary)" }}>Verifying administrator credentials & database connection...</p>
      </div>
    );
  }

  // ── DEDICATED HIGH-SECURITY ADMIN LOGIN CONSOLE ─────────────────────────────
  if (!token || !currentUser || currentUser?.role !== "admin") {
    return (
      <div className="vl-container" style={{ maxWidth: "480px", paddingTop: "3.5rem" }}>
        <div
          className="vl-card"
          style={{
            padding: "2.5rem",
            border: "1px solid rgba(20, 184, 166, 0.25)",
            boxShadow: "0 12px 32px rgba(15, 23, 42, 0.08)",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "14px",
                backgroundColor: "var(--accent-teal-light)",
                color: "var(--accent-teal)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 14px",
              }}
            >
              <Server size={30} strokeWidth={2.2} />
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--accent-teal)",
                marginBottom: "4px",
              }}
            >
              Restricted Identity & Database Access
            </div>
            <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.75rem", fontWeight: 800 }}>
              System Console
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
              Authenticate with authorized credentials to access the internal database and management tools.
            </p>
          </div>

          {errorMsg && (
            <div
              className="vl-fade-in"
              style={{
                backgroundColor: "#FEF2F2",
                border: "1px solid #FCA5A5",
                color: "#B91C1C",
                padding: "10px 14px",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.85rem",
                marginBottom: "1.25rem",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <ShieldAlert size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleAdminLoginSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label htmlFor="sys-console-id" style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Email or Username
              </label>
              <input
                id="sys-console-id"
                type="text"
                required
                value={adminIdentifier}
                onChange={(e) => setAdminIdentifier(e.target.value)}
                placeholder="Enter your credentials"
                className="vl-input"
                style={{ padding: "10px 12px" }}
                aria-label="Email or Username"
              />
            </div>

            <div>
              <label htmlFor="sys-console-pw" style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Password
              </label>
              <input
                id="sys-console-pw"
                type="password"
                required
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                placeholder="••••••••••••"
                className="vl-input"
                style={{ padding: "10px 12px" }}
                aria-label="Password"
              />
            </div>

            <button
              type="submit"
              disabled={adminLoginLoading}
              className="vl-btn vl-btn-primary"
              style={{ width: "100%", padding: "12px", marginTop: "6px" }}
            >
              {adminLoginLoading ? "Verifying Credentials..." : "Unlock Console"}
            </button>
          </form>

          <div style={{ marginTop: "1.5rem", textAlign: "center" }}>
            <Link
              href="/"
              style={{
                fontSize: "0.85rem",
                color: "var(--text-secondary)",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <ArrowLeft size={14} /> Back to Public Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="vl-admin-scope">
      <div className="vl-container" style={{ paddingTop: "2rem" }}>
        {/* Top Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" }}>
              <Server size={18} />
              <span>Database & Identity Console</span>
              <span style={{ backgroundColor: "rgba(13, 148, 136, 0.2)", border: "1px solid var(--accent-teal)", color: "#2DD4BF", fontSize: "0.72rem", padding: "2px 8px", borderRadius: "12px", letterSpacing: "0.05em" }}>
                EXECUTIVE ADMIN
              </span>
            </div>
            <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2rem", fontWeight: 800, color: "#FFFFFF" }}>
              System Command Portal
            </h1>
            <p style={{ color: "#9CA3AF", fontSize: "0.92rem", marginTop: "4px" }}>
              Secure management tier: Live Supabase engine, registered operators, and crowd perception audits.
            </p>
          </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="button"
            className="vl-btn vl-btn-secondary"
            onClick={() => token && loadAdminData(token)}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <RefreshCw size={16} />
            <span>Sync Database</span>
          </button>
          <button
            type="button"
            className="vl-btn vl-btn-outline"
            onClick={() => {
              localStorage.removeItem("visionlytics_token");
              localStorage.removeItem("visionlytics_user");
              setToken(null);
              setCurrentUser(null);
              window.location.href = "/login";
            }}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px", color: "#EF4444", borderColor: "#FCA5A5", cursor: "pointer" }}
          >
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* KPI Overview Cards */}
      {overview && (
        <section className="vl-stats-row" style={{ marginBottom: "2rem" }}>
          <div className="vl-stat-box">
            <div className="vl-stat-icon-wrap" style={{ background: "var(--accent-teal-light)", color: "var(--accent-teal)" }}>
              <Users size={24} />
            </div>
            <div>
              <div className="vl-stat-value">{overview.total_users}</div>
              <div className="vl-stat-label">Registered Accounts</div>
            </div>
          </div>

          <div className="vl-stat-box">
            <div className="vl-stat-icon-wrap" style={{ background: "var(--accent-blue-light)", color: "var(--accent-blue)" }}>
              <Database size={24} />
            </div>
            <div>
              <div className="vl-stat-value">{overview.total_analyses}</div>
              <div className="vl-stat-label">Database Analysis Records</div>
            </div>
          </div>

          <div className="vl-stat-box">
            <div className="vl-stat-icon-wrap" style={{ background: "var(--accent-purple-light)", color: "var(--accent-purple)" }}>
              <ImageIcon size={24} />
            </div>
            <div>
              <div className="vl-stat-value">{overview.total_uploads ?? uploads.length}</div>
              <div className="vl-stat-label">User Image Uploads</div>
            </div>
          </div>

          <div className="vl-stat-box">
            <div className="vl-stat-icon-wrap" style={{ background: "rgba(16, 185, 129, 0.12)", color: "#059669" }}>
              <Activity size={24} />
            </div>
            <div>
              <div className="vl-stat-value">{overview.database_engine}</div>
              <div className="vl-stat-label">Active Database Engine</div>
            </div>
          </div>
        </section>
      )}

      {/* Navigation Tabs */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          borderBottom: "1px solid var(--border-subtle)",
          marginBottom: "1.5rem",
          overflowX: "auto",
        }}
      >
        <button
          type="button"
          onClick={() => setActiveTab("users")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "transparent",
            color: activeTab === "users" ? "var(--accent-teal)" : "var(--text-secondary)",
            borderBottom: activeTab === "users" ? "2px solid var(--accent-teal)" : "2px solid transparent",
            fontWeight: 700,
            fontSize: "0.95rem",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          Users Registry ({users.length})
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("database")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "transparent",
            color: activeTab === "database" ? "var(--accent-teal)" : "var(--text-secondary)",
            borderBottom: activeTab === "database" ? "2px solid var(--accent-teal)" : "2px solid transparent",
            fontWeight: 700,
            fontSize: "0.95rem",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          Analysis History ({analyses.length})
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("uploads")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "transparent",
            color: activeTab === "uploads" ? "var(--accent-teal)" : "var(--text-secondary)",
            borderBottom: activeTab === "uploads" ? "2px solid var(--accent-teal)" : "2px solid transparent",
            fontWeight: 700,
            fontSize: "0.95rem",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          User Uploads ({uploads.length})
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("consent")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "transparent",
            color: activeTab === "consent" ? "var(--accent-teal)" : "var(--text-secondary)",
            borderBottom: activeTab === "consent" ? "2px solid var(--accent-teal)" : "2px solid transparent",
            fontWeight: 700,
            fontSize: "0.95rem",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          Consent Logs ({consentLogs.length})
        </button>
      </div>

      {/* ── TAB 1: USERS REGISTRY ────────────────────────────────────────────── */}
      {activeTab === "users" && (
        <div className="vl-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "10px" }}>
            <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.15rem", fontWeight: 700 }}>
              Registered Users & Authentications
            </h2>
            <div style={{ position: "relative", width: "260px" }}>
              <input
                type="text"
                placeholder="Search username, email, phone..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                className="vl-input"
                style={{ paddingLeft: "34px", fontSize: "0.85rem", padding: "8px 12px 8px 34px" }}
              />
              <Search size={15} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="vl-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Phone Number</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: "2rem" }}>
                      No matching user records found.
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((u) => (
                    <tr key={u.id}>
                      <td style={{ fontWeight: 700 }}>#{u.id}</td>
                      <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{u.username}</td>
                      <td>{u.email}</td>
                      <td>{u.phone || <span style={{ color: "var(--text-muted)" }}>None</span>}</td>
                      <td>
                        <span
                          style={{
                            fontSize: "0.75rem",
                            fontWeight: 700,
                            padding: "3px 8px",
                            borderRadius: "4px",
                            background: u.role === "admin" ? "#FEF3C7" : "#F1F5F9",
                            color: u.role === "admin" ? "#D97706" : "#475569",
                          }}
                        >
                          {u.role.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.82rem", color: u.is_verified ? "#059669" : "#64748B" }}>
                          {u.is_verified ? "Verified" : "Active"}
                        </span>
                      </td>
                      <td style={{ fontSize: "0.82rem" }}>{new Date(u.created_at).toLocaleDateString()}</td>
                      <td>
                        {u.role !== "admin" && (
                          <button
                            type="button"
                            onClick={() => handleDeleteUser(u.id)}
                            style={{
                              background: "transparent",
                              border: "none",
                              color: "#EF4444",
                              cursor: "pointer",
                              padding: "4px",
                            }}
                            title="Delete User"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB 2: CROWD ANALYSIS DATABASE ──────────────────────────────────── */}
      {activeTab === "database" && (
        <div className="vl-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "10px" }}>
            <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.15rem", fontWeight: 700 }}>
              Live Crowd Analysis History ({overview?.database_engine})
            </h2>
            <div style={{ display: "flex", gap: "8px" }}>
              {["ALL", "LOW", "MEDIUM", "HIGH"].map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setAnalysisFilter(lvl)}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    background: analysisFilter === lvl ? "var(--accent-teal)" : "#FFFFFF",
                    color: analysisFilter === lvl ? "#FFFFFF" : "var(--text-secondary)",
                  }}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="vl-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Source</th>
                  <th>People Count</th>
                  <th>Density Regime</th>
                  <th>Occupancy</th>
                  <th>Confidence</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {filteredAnalyses.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: "center", padding: "2rem" }}>
                      No analysis records stored in database yet.
                    </td>
                  </tr>
                ) : (
                  filteredAnalyses.map((a, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 700 }}>#{a.id || idx + 1}</td>
                      <td>
                        <span style={{ textTransform: "capitalize", fontWeight: 500 }}>{a.source_type || "image"}</span>
                      </td>
                      <td style={{ fontWeight: 700, color: "var(--text-primary)" }}>{a.people_count}</td>
                      <td>
                        <span className={`vl-density-badge vl-density-${a.density_label}`}>
                          {a.density_label}
                        </span>
                      </td>
                      <td>{(a.occupancy_ratio * 100).toFixed(1)}%</td>
                      <td>{(a.confidence * 100).toFixed(0)}%</td>
                      <td style={{ fontSize: "0.82rem" }}>
                        {a.created_at || a.timestamp ? new Date(a.created_at || a.timestamp!).toLocaleString() : "Recent"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB 3: USER UPLOADS & IMAGES ────────────────────────────────────── */}
      {activeTab === "uploads" && (
        <div className="vl-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "10px" }}>
            <div>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.15rem", fontWeight: 700 }}>
                User Uploaded Images & Scans
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "2px" }}>
                Full visibility into uploaded frames, thumbnails, detected crowd density, and file metadata.
              </p>
            </div>
            <div style={{ position: "relative", width: "260px" }}>
              <input
                type="text"
                placeholder="Search file, user, email..."
                value={uploadSearch}
                onChange={(e) => setUploadSearch(e.target.value)}
                className="vl-input"
                style={{ paddingLeft: "34px", fontSize: "0.85rem", padding: "8px 12px 8px 34px" }}
              />
              <Search size={15} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
            </div>
          </div>

          {uploads.length === 0 ? (
            <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-secondary)" }}>
              <ImageIcon size={40} style={{ margin: "0 auto 10px", opacity: 0.4 }} />
              <p>No user image uploads recorded in database yet.</p>
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="vl-table">
                <thead>
                  <tr>
                    <th>Preview</th>
                    <th>Filename</th>
                    <th>Uploader</th>
                    <th>People</th>
                    <th>Density</th>
                    <th>Size</th>
                    <th>Uploaded At</th>
                  </tr>
                </thead>
                <tbody>
                  {uploads
                    .filter((u) => {
                      const q = uploadSearch.toLowerCase();
                      return (
                        u.filename.toLowerCase().includes(q) ||
                        u.username.toLowerCase().includes(q) ||
                        u.email.toLowerCase().includes(q)
                      );
                    })
                    .map((up) => (
                      <tr key={up.id}>
                        <td>
                          {up.thumbnail_base64 ? (
                            <img
                              src={up.thumbnail_base64}
                              alt={up.filename}
                              style={{
                                width: "64px",
                                height: "48px",
                                objectFit: "cover",
                                borderRadius: "4px",
                                border: "1px solid var(--border-subtle)",
                              }}
                            />
                          ) : (
                            <div
                              style={{
                                width: "64px",
                                height: "48px",
                                borderRadius: "4px",
                                background: "#F1F5F9",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                color: "#94A3B8",
                              }}
                            >
                              <ImageIcon size={18} />
                            </div>
                          )}
                        </td>
                        <td>
                          <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{up.filename}</div>
                          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{up.content_type}</div>
                        </td>
                        <td>
                          <div style={{ fontWeight: 500 }}>{up.username || "Public User"}</div>
                          {up.email && !up.email.includes("anonymous") ? (
                            <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>{up.email}</div>
                          ) : null}
                        </td>
                        <td style={{ fontWeight: 700, color: "var(--text-primary)" }}>{up.people_count}</td>
                        <td>
                          <span className={`vl-density-badge vl-density-${up.density_label}`}>
                            {up.density_label}
                          </span>
                        </td>
                        <td style={{ fontSize: "0.82rem" }}>
                          {(up.file_size_bytes / 1024).toFixed(1)} KB
                        </td>
                        <td style={{ fontSize: "0.82rem" }}>
                          {new Date(up.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 4: CONSENT LOGS ──────────────────────────────────────────────── */}
      {activeTab === "consent" && (
        <div className="vl-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "10px" }}>
            <div>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.15rem", fontWeight: 700 }}>
                Cookie & GDPR Consent Audit Logs
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "2px" }}>
                Immutable consent audit logs with SHA-256 anonymized IP addresses.
              </p>
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="vl-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Consent Category</th>
                  <th>Analytics Permitted</th>
                  <th>Anonymized Hash</th>
                  <th>Recorded At</th>
                </tr>
              </thead>
              <tbody>
                {consentLogs.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center", padding: "2rem" }}>
                      No consent logs recorded yet.
                    </td>
                  </tr>
                ) : (
                  consentLogs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ fontWeight: 700 }}>#{log.id}</td>
                      <td>
                        <span style={{ fontWeight: 600, textTransform: "capitalize" }}>
                          {log.consent_type}
                        </span>
                      </td>
                      <td>
                        <span
                          style={{
                            fontSize: "0.78rem",
                            fontWeight: 700,
                            padding: "3px 8px",
                            borderRadius: "4px",
                            background: log.analytics_allowed ? "rgba(16, 185, 129, 0.12)" : "rgba(239, 68, 68, 0.12)",
                            color: log.analytics_allowed ? "#059669" : "#DC2626",
                          }}
                        >
                          {log.analytics_allowed ? "Opted In" : "Declined"}
                        </span>
                      </td>
                      <td style={{ fontFamily: "monospace", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                        {log.ip_hash}
                      </td>
                      <td style={{ fontSize: "0.82rem" }}>
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
