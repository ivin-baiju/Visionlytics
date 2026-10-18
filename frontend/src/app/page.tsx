"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  Activity,
  Award,
  Server,
  Image as ImageIcon,
  Video as VideoIcon,
  Camera,
  Brain,
  ArrowRight,
  User,
  LogOut,
  FolderKanban,
  Calendar,
  Layers,
  Database,
  ShieldCheck,
  Lightbulb,
  Sparkles,
  Search,
} from "lucide-react";
import { checkApiHealth } from "@/lib/api";

export default function DashboardPage() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkApiHealth().then(setApiOnline);
  }, []);

  return (
    <div className="vl-container">
      <div className="vl-dashboard-layout">
        {/* ── Left Sidebar (Directly matching Lordicon layout) ───────────────── */}
        <aside className="vl-sidebar">
          <Link href="/" className="vl-sidebar-item active">
            Dashboard
          </Link>
          <Link href="/image-analysis" className="vl-sidebar-item">
            Image Analysis
          </Link>
          <Link href="/video-analysis" className="vl-sidebar-item">
            Video Analysis
          </Link>
          <Link href="/live-camera" className="vl-sidebar-item">
            Live Camera
          </Link>
          <Link href="/ml-models" className="vl-sidebar-item">
            ML Models
          </Link>
          <Link href="/dataset" className="vl-sidebar-item">
            Dataset
          </Link>
          <Link href="/about" className="vl-sidebar-item">
            Documentation
          </Link>
        </aside>

        {/* ── Main Content Area ────────────────────────────────────────────── */}
        <div className="vl-content-panel">
          <div>
            <h1 className="vl-page-title">Dashboard</h1>
            <p className="vl-page-subtitle">Real-time crowd intelligence, model health, and computer vision feeds.</p>
          </div>

          {/* ── User Profile Card (Matched with Lordicon Screenshot) ─────────── */}
          <section className="vl-profile-card">
            <div className="vl-profile-left">
              <div className="vl-profile-avatar-wrap">
                <User size={38} strokeWidth={1.75} />
              </div>
              <div className="vl-profile-meta">
                <span className="vl-tag-pill">STUDENT / RESEARCH</span>
                <h2 className="vl-profile-greeting">Hi there!</h2>
                <span className="vl-profile-id">ivin.baiju@visionlytics.ai</span>
              </div>
            </div>

            <button
              type="button"
              className="vl-btn-outline"
              onClick={() => alert("Session active")}
            >
              <LogOut size={16} />
              <span>Log out</span>
            </button>
          </section>

          {/* ── 3-Up KPI Stat Cards (Directly matching Lordicon layout) ────────── */}
          <section className="vl-stats-row">
            <div className="vl-stat-box">
              <div className="vl-stat-icon-wrap">
                <Users size={24} strokeWidth={1.8} />
              </div>
              <div>
                <div className="vl-stat-value">1,482</div>
                <div className="vl-stat-label">total detected persons</div>
              </div>
            </div>

            <div className="vl-stat-box">
              <div className="vl-stat-icon-wrap">
                <Calendar size={24} strokeWidth={1.8} />
              </div>
              <div>
                <div className="vl-stat-value">94.2%</div>
                <div className="vl-stat-label">classifier test accuracy</div>
              </div>
            </div>

            <div className="vl-stat-box">
              <div className="vl-stat-icon-wrap">
                <FolderKanban size={24} strokeWidth={1.8} />
              </div>
              <div>
                <div className="vl-stat-value">
                  {apiOnline === null ? "..." : apiOnline ? "Online" : "Local"}
                </div>
                <div className="vl-stat-label">
                  {apiOnline ? "FastAPI localhost:8000" : "simulation fallback"}
                </div>
              </div>
            </div>
          </section>

          {/* ── Notifications / System Status Banner (Matching Lordicon) ──────── */}
          <h2 className="vl-section-header">Notifications</h2>
          <section className="vl-banner-card">
            <div className="vl-banner-left">
              <div className="vl-banner-icon">
                <ShieldCheck size={22} />
              </div>
              <div>
                <div className="vl-banner-title">Surveillance & Pipeline Integrity Verified</div>
                <div className="vl-banner-desc">YOLOv8s detector, 10D feature extractor, and Random Forest ensemble ready for inference.</div>
              </div>
            </div>
            <Link href="/image-analysis" className="vl-btn-outline">
              Inspect Pipeline
            </Link>
          </section>

          {/* ── Learn more / Workspaces (Matching Lordicon 3-Grid) ─────────────── */}
          <h2 className="vl-section-header">Workspaces & Analysis</h2>
          <section className="vl-feature-grid">
            <Link href="/image-analysis" className="vl-feature-card">
              <div className="vl-feature-icon-circle vl-feature-icon-purple">
                <Lightbulb size={22} />
              </div>
              <h3 className="vl-feature-title">Image Analysis</h3>
              <p className="vl-feature-desc">
                Upload crowd photography to generate spatial density contours, 10 geometric features, and regime labels.
              </p>
              <div className="vl-feature-arrow">
                Launch tool <ArrowRight size={14} />
              </div>
            </Link>

            <Link href="/video-analysis" className="vl-feature-card">
              <div className="vl-feature-icon-circle vl-feature-icon-teal">
                <Sparkles size={22} />
              </div>
              <h3 className="vl-feature-title">Video Surveillance</h3>
              <p className="vl-feature-desc">
                Process video clips with centroid trajectory tracking, crowd flow charts, and threshold alert triggers.
              </p>
              <div className="vl-feature-arrow">
                Launch stream <ArrowRight size={14} />
              </div>
            </Link>

            <Link href="/live-camera" className="vl-feature-card">
              <div className="vl-feature-icon-circle vl-feature-icon-blue">
                <Search size={22} />
              </div>
              <h3 className="vl-feature-title">Live Camera</h3>
              <p className="vl-feature-desc">
                Connect your webcam for low-latency live crowd monitoring, bounding box tracking, and real-time FPS metrics.
              </p>
              <div className="vl-feature-arrow">
                Connect webcam <ArrowRight size={14} />
              </div>
            </Link>
          </section>

          {/* ── Technical Overview ────────────────────────────────────────────── */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem", marginTop: "0.5rem" }}>
            <div className="vl-card">
              <div className="vl-card-header">
                <span className="vl-card-label">Density Regimes Breakdown</span>
                <Layers size={18} color="var(--accent-teal)" />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "4px" }}>
                    <span style={{ color: "#059669", fontWeight: 600 }}>Low Density (0–5 persons)</span>
                    <span style={{ fontWeight: 600, color: "var(--text-secondary)" }}>42%</span>
                  </div>
                  <div style={{ height: "6px", background: "#F1F5F9", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ width: "42%", height: "100%", background: "#10B981", borderRadius: "4px" }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "4px" }}>
                    <span style={{ color: "#D97706", fontWeight: 600 }}>Medium Density (6–15 persons)</span>
                    <span style={{ fontWeight: 600, color: "var(--text-secondary)" }}>38%</span>
                  </div>
                  <div style={{ height: "6px", background: "#F1F5F9", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ width: "38%", height: "100%", background: "#F59E0B", borderRadius: "4px" }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "4px" }}>
                    <span style={{ color: "#DC2626", fontWeight: 600 }}>High Density (&gt;15 persons)</span>
                    <span style={{ fontWeight: 600, color: "var(--text-secondary)" }}>20%</span>
                  </div>
                  <div style={{ height: "6px", background: "#F1F5F9", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ width: "20%", height: "100%", background: "#EF4444", borderRadius: "4px" }} />
                  </div>
                </div>
              </div>
            </div>

            <div className="vl-card">
              <div className="vl-card-header">
                <span className="vl-card-label">Architecture Pipeline</span>
                <Database size={18} color="var(--accent-teal)" />
              </div>
              <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.88rem", color: "var(--text-secondary)" }}>
                <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#0D9488" }} />
                  <strong>Stage 1 (Perception):</strong> Ultralytics YOLOv8s with ByteTrack
                </li>
                <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#0284C7" }} />
                  <strong>Stage 2 (Features):</strong> 10D geometric, Voronoi & spatial distribution
                </li>
                <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#8B5CF6" }} />
                  <strong>Stage 3 (Inference):</strong> Calibrated Statistical ML Classifiers
                </li>
                <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#10B981" }} />
                  <strong>Stage 4 (Fallback):</strong> CSRNet Dilated CNN for high occlusion
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
