"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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

export default function AdminPortalPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Database Tab
  const [activeTab, setActiveTab] = useState<"users" | "database" | "security">("users");

  // Data states
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [analyses, setAnalyses] = useState<AdminAnalysis[]>([]);
  const [overview, setOverview] = useState<{
    total_users: number;
    total_analyses: number;
    total_people_detected: number;
    database_engine: string;
  } | null>(null);

  // Search filter
  const [userSearch, setUserSearch] = useState("");
  const [analysisFilter, setAnalysisFilter] = useState("ALL");

  const loadAdminData = React.useCallback(async (authToken: string) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const headers = { Authorization: `Bearer ${authToken}` };

      const [ovRes, uRes, aRes] = await Promise.all([
        fetch("/api/py/admin/database/overview", { headers }),
        fetch("/api/py/admin/users", { headers }),
        fetch("/api/py/admin/database/analyses", { headers }),
      ]);

      if (ovRes.status === 401 || ovRes.status === 403) {
        setErrorMsg("Session expired or unauthorized. Please sign in with an Admin account.");
        setLoading(false);
        return;
      }

      const ovData = await ovRes.json();
      const uData = await uRes.json();
      const aData = await aRes.json();

      setOverview(ovData);
      setUsers(uData.users || []);
      setAnalyses(aData.analyses || []);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to load database records.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const frameId = requestAnimationFrame(() => {
      const savedToken = localStorage.getItem("visionlytics_token");
      const savedUserStr = localStorage.getItem("visionlytics_user");

      if (!savedToken) {
        router.push("/login?error=admin_required");
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
        router.push("/login");
      }
    });

    return () => cancelAnimationFrame(frameId);
  }, [router, loadAdminData]);

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

  if (errorMsg) {
    return (
      <div className="vl-container" style={{ maxWidth: "600px", paddingTop: "4rem" }}>
        <div className="vl-card" style={{ textAlign: "center", padding: "2.5rem" }}>
          <ShieldAlert size={44} color="#EF4444" style={{ margin: "0 auto 1rem" }} />
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.5rem", fontWeight: 800 }}>
            Restricted Admin Console
          </h2>
          <p style={{ color: "var(--text-secondary)", margin: "1rem 0 1.5rem" }}>{errorMsg}</p>
          <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
            <Link href="/login" className="vl-btn vl-btn-primary">
              Sign In as Admin
            </Link>
            <Link href="/" className="vl-btn vl-btn-secondary">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="vl-container">
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "6px" }}>
            <Server size={18} />
            Master Database & Identity Console
          </div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2rem", fontWeight: 800 }}>
            Administrator Portal
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
            Full access to users registry, live Supabase tables, and crowd analytics records.
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
          <Link href="/" className="vl-btn vl-btn-outline" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <ArrowLeft size={16} />
            <span>Dashboard</span>
          </Link>
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
          }}
        >
          Analysis History ({analyses.length})
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
    </div>
  );
}
