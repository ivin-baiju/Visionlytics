"use client";

import React, { useState, useEffect } from "react";
import { Database, RefreshCw, Filter, Layers, CheckCircle, AlertTriangle } from "lucide-react";
import { getDatasetInfoApi, getDatasetPreviewApi, triggerDatasetGenerateApi } from "@/lib/api";

export default function DatasetPage() {
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [info, setInfo] = useState<{ total: number; classCounts: Record<string, number> } | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<(number | string)[][]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [meta, preview] = await Promise.all([getDatasetInfoApi(), getDatasetPreviewApi(8)]);
        if (cancelled) return;
        setInfo({ total: meta.n_rows, classCounts: meta.class_counts });
        setColumns(preview.columns);
        setRows(preview.rows);
      } catch (err) {
        if (!cancelled) setApiError(err instanceof Error ? err.message : "Failed to load dataset");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setApiError(null);
    try {
      const preview = await triggerDatasetGenerateApi(500);
      setInfo({ total: preview.n_rows, classCounts: preview.class_counts });
      setColumns(preview.columns);
      setRows(preview.rows.slice(0, 8));
      setSuccess(`Dataset regenerated! ${preview.n_rows} spatial records re-computed and saved.`);
      setTimeout(() => setSuccess(null), 4000);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Dataset regeneration failed");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="vl-container">
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
          {success}
        </div>
      )}

      {apiError && (
        <div role="alert" style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#DC2626", padding: "12px 18px", borderRadius: "12px", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "10px", fontSize: "0.9rem", fontWeight: 600 }}>
          <AlertTriangle size={18} /> {apiError} — start the backend with `python start_local.py`.
        </div>
      )}

      {/* Overview Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.25rem", marginBottom: "2rem" }}>
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Total Sample Size</span>
            <Database size={18} color="var(--accent-blue)" />
          </div>
          <div className="vl-kpi-value">{isLoading ? "…" : (info?.total.toLocaleString() ?? "—")}</div>
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
          <div className="vl-kpi-value">
            {info ? ["LOW", "MEDIUM", "HIGH"].map((k) => info.classCounts[k] ?? 0).join(" / ") : "—"}
          </div>
          <div className="vl-kpi-subtitle">LOW / MEDIUM / HIGH counts</div>
        </div>
      </div>

      {/* Dataset Table Preview */}
      <div className="vl-card">
        <div className="vl-card-header">
          <span className="vl-card-label">Feature Vector Samples</span>
          <span style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>
            {rows.length > 0 && info ? `Showing ${rows.length} of ${info.total.toLocaleString()} rows` : "Live preview from backend"}
          </span>
        </div>

        <div style={{ overflowX: "auto" }}>
          {isLoading ? (
            <p style={{ padding: "1.5rem", textAlign: "center" }}>Loading dataset preview…</p>
          ) : rows.length === 0 ? (
            <p style={{ padding: "1.5rem", textAlign: "center" }}>No rows available.</p>
          ) : (
          <table className="vl-table">
            <thead>
              <tr>
                {columns.map((c) => (
                  <th key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => {
                    const col = columns[j] ?? "";
                    if (col === "density_label") {
                      return (
                        <td key={j}>
                          <span className={`vl-density-badge vl-density-${cell}`}>{cell}</span>
                        </td>
                      );
                    }
                    return <td key={j}>{typeof cell === "number" ? (Number.isInteger(cell) ? cell : cell.toFixed(4)) : cell}</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          )}
        </div>
      </div>
    </div>
  );
}
