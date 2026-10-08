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
  Database,
  Layers,
} from "lucide-react";
import KpiCard from "@/components/KpiCard";
import { checkApiHealth } from "@/lib/api";

export default function DashboardPage() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkApiHealth().then(setApiOnline);
  }, []);

  return (
    <div className="vl-main-content">
      {/* ── Hero Section ─────────────────────────────────────────────────── */}
      <section className="vl-hero">
        <div className="vl-hero-header">
          <div className="vl-hero-badge-wrap">
            <div className="vl-hero-badge-inner">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/logo.svg" alt="Visionlytics" width={42} height={42} />
            </div>
          </div>
          <div className="vl-hero-title-group">
            <h1>VISIONLYTICS</h1>
            <p>Intelligent Visual Crowd Analytics & Machine Learning Platform</p>
          </div>
        </div>

        <div className="vl-badge-row">
          <span className="vl-badge live">
            <span className="vl-pulse-dot" />
            System Live
          </span>
          <span className="vl-badge">YOLOv8s Detector</span>
          <span className="vl-badge">Multi-Model ML Suite</span>
          <span className="vl-badge">Spatial Density Map</span>
          <span className="vl-badge">CSRNet Deep Head</span>
        </div>
      </section>

      {/* ── KPI Grid ─────────────────────────────────────────────────────── */}
      <section className="vl-kpi-grid">
        <KpiCard
          label="Total Crowd Detections"
          value="1,482"
          subtitle="Across active sessions"
          icon={<Users size={20} />}
          trend="↑ +12%"
        />
        <KpiCard
          label="Engine Inference Latency"
          value="24 ms"
          subtitle="YOLOv8s + spatial extractor"
          icon={<Activity size={20} />}
        />
        <KpiCard
          label="Champion Model Accuracy"
          value="94.2%"
          subtitle="Random Forest Classifier"
          icon={<Award size={20} />}
          trend="Held-out Test"
        />
        <KpiCard
          label="FastAPI Microservice"
          value={apiOnline === null ? "Probing..." : apiOnline ? "Connected" : "Simulated"}
          subtitle={apiOnline ? "FastAPI localhost:8000" : "Standalone client engine active"}
          icon={<Server size={20} />}
        />
      </section>

      {/* ── Quick Action Cards ───────────────────────────────────────────── */}
      <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.4rem", fontWeight: 700, marginBottom: "1rem" }}>
        Analytics Workspaces
      </h2>
      <section className="vl-actions-grid">
        <Link href="/image-analysis" className="vl-action-card">
          <div className="vl-action-icon">
            <ImageIcon size={22} />
          </div>
          <h3 className="vl-action-title">Image Analysis</h3>
          <p className="vl-action-desc">
            Upload high-resolution crowd photographs to detect persons, extract 10 geometric features, and infer density regimes.
          </p>
          <span className="vl-action-arrow">
            Open workspace <ArrowRight size={15} />
          </span>
        </Link>

        <Link href="/video-analysis" className="vl-action-card">
          <div className="vl-action-icon">
            <VideoIcon size={22} />
          </div>
          <h3 className="vl-action-title">Video Analysis</h3>
          <p className="vl-action-desc">
            Stream and evaluate recorded surveillance footage with persistent centroid trajectory tracking and temporal flow graphs.
          </p>
          <span className="vl-action-arrow">
            Launch stream <ArrowRight size={15} />
          </span>
        </Link>

        <Link href="/live-camera" className="vl-action-card">
          <div className="vl-action-icon">
            <Camera size={22} />
          </div>
          <h3 className="vl-action-title">Live Camera</h3>
          <p className="vl-action-desc">
            Direct WebRTC camera feed with live real-time bounding boxes, FPS counters, and instant density alert triggers.
          </p>
          <span className="vl-action-arrow">
            Connect camera <ArrowRight size={15} />
          </span>
        </Link>

        <Link href="/ml-models" className="vl-action-card">
          <div className="vl-action-icon">
            <Brain size={22} />
          </div>
          <h3 className="vl-action-title">ML Models & Benchmarks</h3>
          <p className="vl-action-desc">
            Explore the comparative evaluation suite of 7 statistical models: Random Forest, SVM, Gradient Boosting, and Ensembles.
          </p>
          <span className="vl-action-arrow">
            View leaderboard <ArrowRight size={15} />
          </span>
        </Link>
      </section>

      {/* ── System Overview Grid ─────────────────────────────────────────── */}
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "1.5rem" }}>
        {/* Real-Time Density Regimes */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Density Classification Regimes</span>
            <Layers size={18} color="var(--accent-blue)" />
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", marginBottom: "1.25rem" }}>
            Real-world crowd distribution breakdown calibrated across the dataset:
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "4px" }}>
                <span style={{ color: "var(--accent-emerald)", fontWeight: 600 }}>LOW DENSITY (0–5 persons)</span>
                <span>42%</span>
              </div>
              <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "42%", height: "100%", background: "var(--accent-emerald)", borderRadius: "4px" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "4px" }}>
                <span style={{ color: "var(--accent-amber)", fontWeight: 600 }}>MEDIUM DENSITY (6–15 persons)</span>
                <span>38%</span>
              </div>
              <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "38%", height: "100%", background: "var(--accent-amber)", borderRadius: "4px" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "4px" }}>
                <span style={{ color: "var(--accent-rose)", fontWeight: 600 }}>HIGH DENSITY (&gt;15 persons)</span>
                <span>20%</span>
              </div>
              <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "20%", height: "100%", background: "var(--accent-rose)", borderRadius: "4px" }} />
              </div>
            </div>
          </div>
        </div>

        {/* Dataset & Architecture Spec */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Pipeline Architecture</span>
            <Database size={18} color="var(--accent-indigo)" />
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", marginBottom: "1rem" }}>
            Next-generation two-stage hybrid design:
          </p>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-blue)" }} />
              <strong>Stage 1 (Perception):</strong> Ultralytics YOLOv8s with ByteTrack
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-indigo)" }} />
              <strong>Stage 2 (Features):</strong> 10D geometric, Voronoi & spatial distribution
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-purple)" }} />
              <strong>Stage 3 (Inference):</strong> Calibrated Statistical ML Classifiers
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-emerald)" }} />
              <strong>Stage 4 (Fallback):</strong> CSRNet Dilated CNN for extreme congestion
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
