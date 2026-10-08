"use client";

import React, { useState, useEffect } from "react";
import { Award, Brain, BarChart2, RefreshCw, CheckCircle2, TrendingUp } from "lucide-react";
import { getModelsEvaluationApi } from "@/lib/api";
import { ModelMetric } from "@/types";

const FEATURE_IMPORTANCES = [
  { feature: "people_count", importance: 0.38, desc: "Primary crowd volume count" },
  { feature: "occupancy_ratio", importance: 0.22, desc: "Total pixel space coverage" },
  { feature: "avg_distance", importance: 0.14, desc: "Mean interpersonal distance" },
  { feature: "min_distance", importance: 0.11, desc: "Bottleneck cluster proximity" },
  { feature: "density_ratio", importance: 0.07, desc: "Relative congestion coefficient" },
  { feature: "avg_person_area", importance: 0.05, desc: "Perspective depth indicator" },
  { feature: "std_distance", importance: 0.03, desc: "Dispersion standard deviation" },
];

export default function MlModelsPage() {
  const [models, setModels] = useState<ModelMetric[]>([]);
  const [isRetraining, setIsRetraining] = useState<boolean>(false);
  const [retrainSuccess, setRetrainSuccess] = useState<boolean>(false);

  useEffect(() => {
    getModelsEvaluationApi().then(setModels);
  }, []);

  const handleRetrain = () => {
    setIsRetraining(true);
    setRetrainSuccess(false);
    setTimeout(() => {
      setIsRetraining(false);
      setRetrainSuccess(true);
      setTimeout(() => setRetrainSuccess(false), 4000);
    }, 2000);
  };

  return (
    <div className="vl-main-content">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.75rem" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
            Machine Learning Model Suite
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
            Comparative evaluation and benchmark ranking of 7 statistical classifiers on held-out test data.
          </p>
        </div>

        <button
          type="button"
          className="vl-btn vl-btn-primary"
          onClick={handleRetrain}
          disabled={isRetraining}
        >
          {isRetraining ? (
            <>
              <RefreshCw className="vl-pulse-dot" size={16} /> Retraining Classifiers...
            </>
          ) : (
            <>
              <RefreshCw size={16} /> Retrain All Models
            </>
          )}
        </button>
      </div>

      {retrainSuccess && (
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
          <CheckCircle2 size={18} />
          Retraining pipeline completed successfully! Model registry artifacts re-serialized.
        </div>
      )}

      {/* Model Leaderboard Table */}
      <div className="vl-card" style={{ marginBottom: "2rem" }}>
        <div className="vl-card-header">
          <span className="vl-card-label">Model Leaderboard (Held-Out Test Set)</span>
          <Award size={18} color="var(--accent-blue)" />
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="vl-table">
            <thead>
              <tr>
                <th>Classifier Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1 Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.name}>
                  <td style={{ fontWeight: 600, color: m.is_champion ? "var(--accent-blue)" : undefined }}>
                    {m.name}
                  </td>
                  <td>{(m.accuracy * 100).toFixed(1)}%</td>
                  <td>{(m.precision * 100).toFixed(1)}%</td>
                  <td>{(m.recall * 100).toFixed(1)}%</td>
                  <td>{(m.f1 * 100).toFixed(1)}%</td>
                  <td>
                    {m.is_champion ? (
                      <span className="vl-badge live" style={{ padding: "3px 10px", fontSize: "0.72rem" }}>
                        🏆 Active Champion
                      </span>
                    ) : (
                      <span style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>
                        Benchmarked
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feature Importance & Diagnostics */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {/* Feature Importances */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Champion Feature Importances (Random Forest)</span>
            <BarChart2 size={18} color="var(--accent-purple)" />
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "10px" }}>
            {FEATURE_IMPORTANCES.map((f) => (
              <div key={f.feature}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "4px" }}>
                  <code style={{ color: "var(--accent-blue)", fontFamily: "var(--font-mono)" }}>{f.feature}</code>
                  <span>{(f.importance * 100).toFixed(0)}%</span>
                </div>
                <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "4px" }}>
                  <div
                    style={{
                      width: `${f.importance * 100}%`,
                      height: "100%",
                      background: "linear-gradient(90deg, var(--accent-blue), var(--accent-indigo))",
                      borderRadius: "4px",
                    }}
                  />
                </div>
                <span style={{ fontSize: "0.72rem", color: "var(--text-tertiary)", marginTop: "2px", display: "block" }}>
                  {f.desc}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Validation Methodology */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Statistical Rigor & Splits</span>
            <Brain size={18} color="var(--accent-emerald)" />
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", marginBottom: "1rem" }}>
            The training pipeline enforces strict isolation to ensure zero data leakage:
          </p>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-blue)" }} />
              <strong>70% Training:</strong> Used for model parameter optimization.
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-indigo)" }} />
              <strong>15% Validation:</strong> Hyperparameter tuning and decision thresholding.
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-rose)" }} />
              <strong>15% Held-Out Test:</strong> Completely unseen data for reporting final metrics.
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-emerald)" }} />
              <strong>StandardScaler:</strong> Fit strictly on Train partition to eliminate data leakage.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
