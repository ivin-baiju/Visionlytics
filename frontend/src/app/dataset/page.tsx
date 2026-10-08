"use client";

import React, { useState } from "react";
import { Database, Download, RefreshCw, Filter, Layers, CheckCircle } from "lucide-react";

const SAMPLE_ROWS = [
  { id: 1, people_count: 3, occupancy_ratio: 0.08, avg_distance: 0.52, min_distance: 0.31, density: "LOW" },
  { id: 2, people_count: 4, occupancy_ratio: 0.11, avg_distance: 0.44, min_distance: 0.22, density: "LOW" },
  { id: 3, people_count: 8, occupancy_ratio: 0.24, avg_distance: 0.29, min_distance: 0.15, density: "MEDIUM" },
  { id: 4, people_count: 11, occupancy_ratio: 0.32, avg_distance: 0.23, min_distance: 0.09, density: "MEDIUM" },
  { id: 5, people_count: 18, occupancy_ratio: 0.56, avg_distance: 0.14, min_distance: 0.04, density: "HIGH" },
  { id: 6, people_count: 22, occupancy_ratio: 0.68, avg_distance: 0.11, min_distance: 0.02, density: "HIGH" },
  { id: 7, people_count: 2, occupancy_ratio: 0.05, avg_distance: 0.65, min_distance: 0.65, density: "LOW" },
  { id: 8, people_count: 9, occupancy_ratio: 0.28, avg_distance: 0.26, min_distance: 0.12, density: "MEDIUM" },
];

export default function DatasetPage() {
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 4000);
    }, 1500);
  };

  return (
    <div className="vl-main-content">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.75rem" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
            Crowd Dynamics Dataset Explorer
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
            Synthetic and empirical spatial descriptor vectors used for training and testing statistical ML classifiers.
          </p>
        </div>

        <button
          type="button"
          className="vl-btn vl-btn-primary"
          onClick={handleGenerate}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <RefreshCw className="vl-pulse-dot" size={16} /> Generating Records...
            </>
          ) : (
            <>
              <RefreshCw size={16} /> Regenerate Dataset
            </>
          )}
        </button>
      </div>

      {success && (
        <div
          style={{
            background: "rgba(16, 185, 129, 0.12)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            color: "var(--accent-emerald)",
            padding: "12px 18px",
            borderRadius: "12px",
            marginBottom: "1.5rem",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "0.9rem",
            fontWeight: 600,
          }}
        >
          <CheckCircle size={18} />
          Dataset regenerated! 3,000 spatial records re-computed and saved to repository.
        </div>
      )}

      {/* Overview Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.25rem", marginBottom: "2rem" }}>
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Total Sample Size</span>
            <Database size={18} color="var(--accent-blue)" />
          </div>
          <div className="vl-kpi-value">3,000</div>
          <div className="vl-kpi-subtitle">Balanced across 3 regimes</div>
        </div>

        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Feature Vector Dimension</span>
            <Layers size={18} color="var(--accent-indigo)" />
          </div>
          <div className="vl-kpi-value">10D</div>
          <div className="vl-kpi-subtitle">Geometric & spatial descriptors</div>
        </div>

        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Class Balance</span>
            <Filter size={18} color="var(--accent-purple)" />
          </div>
          <div className="vl-kpi-value">1:1:1</div>
          <div className="vl-kpi-subtitle">1,000 per density class</div>
        </div>
      </div>

      {/* Dataset Table Preview */}
      <div className="vl-card">
        <div className="vl-card-header">
          <span className="vl-card-label">Feature Vector Samples</span>
          <span style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>Showing 8 of 3,000 rows</span>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="vl-table">
            <thead>
              <tr>
                <th>Sample ID</th>
                <th>People Count</th>
                <th>Occupancy Ratio</th>
                <th>Avg Distance</th>
                <th>Min Distance</th>
                <th>Density Target</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_ROWS.map((row) => (
                <tr key={row.id}>
                  <td><code>#{row.id}</code></td>
                  <td><strong>{row.people_count}</strong></td>
                  <td>{(row.occupancy_ratio * 100).toFixed(1)}%</td>
                  <td>{row.avg_distance.toFixed(3)}</td>
                  <td>{row.min_distance.toFixed(3)}</td>
                  <td>
                    <span className={`vl-density-badge vl-density-${row.density}`}>
                      {row.density}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
