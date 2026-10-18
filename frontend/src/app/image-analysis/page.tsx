"use client";

import React, { useState, useRef, useCallback, useMemo, useEffect } from "react";
import {
  Upload,
  Sliders,
  RefreshCw,
  Sparkles,
  Eye,
  Info,
  ImageIcon,
  Flame,
  Download,
  Filter,
  Layers,
  CheckCircle,
  FileSpreadsheet,
  FileJson,
} from "lucide-react";
import BoundingBoxCanvas from "@/components/BoundingBoxCanvas";
import { analyzeFrameApi } from "@/lib/api";
import { FrameAnalysisResult, DensityLabel } from "@/types";

const SAMPLES = [
  {
    name: "Urban Crossing (Moderate)",
    url: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1000&auto=format&fit=crop&q=80",
  },
  {
    name: "Subway Station (Dense)",
    url: "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=1000&auto=format&fit=crop&q=80",
  },
  {
    name: "Public Plaza (Sparse)",
    url: "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1000&auto=format&fit=crop&q=80",
  },
];

export default function ImageAnalysisPage() {
  const [selectedImage, setSelectedImage] = useState<string>(SAMPLES[0].url);
  const [confidence, setConfidence] = useState<number>(0.3);
  const [tracking, setTracking] = useState<boolean>(true);
  const [attributes, setAttributes] = useState<boolean>(true);

  // Power Controls
  const [showHeatmap, setShowHeatmap] = useState<boolean>(false);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [showCentroids, setShowCentroids] = useState<boolean>(true);
  const [minConfidenceFilter, setMinConfidenceFilter] = useState<number>(0.2);

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [result, setResult] = useState<FrameAnalysisResult | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const prevObjectUrl = useRef<string | null>(null);

  const revokePrevUrl = useCallback(() => {
    if (prevObjectUrl.current) {
      URL.revokeObjectURL(prevObjectUrl.current);
      prevObjectUrl.current = null;
    }
  }, []);

  // Revoke blob URLs on unmount to avoid leaks.
  useEffect(() => {
    return () => {
      if (prevObjectUrl.current) URL.revokeObjectURL(prevObjectUrl.current);
    };
  }, []);

  const setImageWithCleanup = useCallback((url: string, objectUrl: string | null) => {
    revokePrevUrl();
    prevObjectUrl.current = objectUrl;
    setSelectedImage(url);
  }, [revokePrevUrl]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setImageWithCleanup(url, url);
      runAnalysis(file);
    }
    // Reset so the same file can be picked twice in a row.
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setImageWithCleanup(url, url);
      runAnalysis(file);
    }
  };

  const runAnalysis = async (fileOrBlob?: Blob) => {
    setIsAnalyzing(true);
    setApiError(null);
    try {
      let blob: Blob;
      if (fileOrBlob) {
        blob = fileOrBlob;
      } else {
        const res = await fetch(selectedImage);
        if (!res.ok) throw new Error(`Sample image fetch failed (${res.status})`);
        blob = await res.blob();
      }

      const data = await analyzeFrameApi(blob, confidence, tracking, attributes);
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult(null);
      setApiError(err instanceof Error ? err.message : "Analysis failed. Is the backend running?");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Filter detections live
  const filteredDetections = useMemo(() => {
    if (!result?.detections) return [];
    return result.detections.filter((d) => d.confidence >= minConfidenceFilter);
  }, [result, minConfidenceFilter]);

  // Export JSON Report
  const exportJsonReport = () => {
    if (!result) return;
    const jsonStr = JSON.stringify(result, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `visionlytics_analysis_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export CSV Report
  const exportCsvReport = () => {
    if (!result) return;
    let csv = "person_id,confidence,x1,y1,x2,y2,hair_color,clothing_color\n";
    filteredDetections.forEach((d, idx) => {
      const [x1, y1, x2, y2] = d.bbox;
      const attr = result.attributes?.[idx];
      csv += `${d.person_id ?? idx + 1},${d.confidence},${x1.toFixed(1)},${y1.toFixed(1)},${x2.toFixed(1)},${y2.toFixed(1)},${attr?.hair_color ?? "N/A"},${attr?.clothing_color ?? "N/A"}\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `visionlytics_detections_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="vl-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.75rem", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h1 className="vl-page-title">Image Inspector</h1>
          <p className="vl-page-subtitle">
            Upload crowd photography to run YOLOv8s person detection, spatial density heatmaps, and 10D feature vector extraction.
          </p>
        </div>

        {/* Export Actions */}
        {result && (
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="button"
              className="vl-btn-outline"
              onClick={exportCsvReport}
              title="Download CSV"
            >
              <FileSpreadsheet size={15} color="#0D9488" />
              <span>Export CSV</span>
            </button>
            <button
              type="button"
              className="vl-btn-outline"
              onClick={exportJsonReport}
              title="Download JSON Report"
            >
              <FileJson size={15} color="#8B5CF6" />
              <span>Export JSON</span>
            </button>
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.75rem", alignItems: "start" }}>
        {/* Left Column: Canvas + Visual Toggles */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Main Visualizer Canvas */}
          <div className="vl-card" style={{ padding: "1.25rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <ImageIcon size={18} color="var(--accent-teal)" />
                <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>Live Canvas View</span>
              </div>

              {/* Visualization Mode Toggles */}
              <div style={{ display: "flex", gap: "6px" }}>
                <button
                  type="button"
                  className={`vl-btn-outline ${showHeatmap ? "active" : ""}`}
                  style={{
                    padding: "6px 12px",
                    fontSize: "0.82rem",
                    borderColor: showHeatmap ? "var(--accent-teal)" : "var(--border-subtle)",
                    backgroundColor: showHeatmap ? "var(--accent-teal-light)" : "#FFFFFF",
                    color: showHeatmap ? "var(--accent-teal)" : "var(--text-secondary)",
                  }}
                  onClick={() => setShowHeatmap((prev) => !prev)}
                >
                  <Flame size={14} /> Heatmap
                </button>
                <button
                  type="button"
                  className="vl-btn-outline"
                  style={{
                    padding: "6px 12px",
                    fontSize: "0.82rem",
                    borderColor: showBoxes ? "var(--accent-teal)" : "var(--border-subtle)",
                    backgroundColor: showBoxes ? "var(--accent-teal-light)" : "#FFFFFF",
                    color: showBoxes ? "var(--accent-teal)" : "var(--text-secondary)",
                  }}
                  onClick={() => setShowBoxes((prev) => !prev)}
                >
                  Boxes
                </button>
                <button
                  type="button"
                  className="vl-btn-outline"
                  style={{
                    padding: "6px 12px",
                    fontSize: "0.82rem",
                    borderColor: showCentroids ? "var(--accent-teal)" : "var(--border-subtle)",
                    backgroundColor: showCentroids ? "var(--accent-teal-light)" : "#FFFFFF",
                    color: showCentroids ? "var(--accent-teal)" : "var(--text-secondary)",
                  }}
                  onClick={() => setShowCentroids((prev) => !prev)}
                >
                  Centroids
                </button>
              </div>
            </div>

            <BoundingBoxCanvas
              imageSrc={selectedImage}
              detections={filteredDetections}
              attributes={result?.attributes}
              showAttributes={attributes}
              showHeatmap={showHeatmap}
              showBoxes={showBoxes}
              showCentroids={showCentroids}
            />

            {/* Quick Presets */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "1rem" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--text-tertiary)", fontWeight: 600 }}>
                Sample Presets:
              </span>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {SAMPLES.map((sample, i) => (
                  <button
                    key={i}
                    type="button"
                    className="vl-btn-outline"
                    style={{
                      padding: "5px 12px",
                      fontSize: "0.8rem",
                      borderColor: selectedImage === sample.url ? "var(--accent-teal)" : "var(--border-subtle)",
                      background: selectedImage === sample.url ? "var(--accent-teal-light)" : "#FFFFFF",
                      color: selectedImage === sample.url ? "var(--accent-teal)" : "var(--text-secondary)",
                    }}
                    onClick={() => {
                      setImageWithCleanup(sample.url, null);
                      setResult(null);
                    }}
                  >
                    {sample.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Drag & Drop Upload Box */}
          <div
            className={`vl-upload-box ${isDragging ? "dragging" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: "none" }}
              accept="image/*"
              onChange={handleFileUpload}
            />
            <Upload size={32} strokeWidth={1.8} style={{ margin: "0 auto 10px", color: "var(--accent-teal)" }} />
            <h4 style={{ fontWeight: 700, fontSize: "0.98rem", marginBottom: "4px" }}>
              Click or drag a crowd image to upload
            </h4>
            <p style={{ color: "var(--text-tertiary)", fontSize: "0.84rem" }}>
              Supports JPG, PNG, WebP up to 25MB
            </p>
          </div>

          {/* 10-Dimensional Spatial Features Breakdown */}
          {result && (
            <div className="vl-card">
              <div className="vl-card-header">
                <span className="vl-card-label">10-Dimensional Spatial Feature Vector</span>
                <Layers size={18} color="var(--accent-teal)" />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "10px" }}>
                {Object.entries(result.features).map(([key, val]) => (
                  <div
                    key={key}
                    style={{
                      padding: "10px 14px",
                      background: "#F8FAFC",
                      borderRadius: "8px",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    <span style={{ fontSize: "0.74rem", color: "var(--text-tertiary)", textTransform: "uppercase", display: "block" }}>
                      {key.replace(/_/g, " ")}
                    </span>
                    <strong style={{ fontSize: "1.05rem", color: "#0F172A" }}>
                      {typeof val === "number" ? val.toFixed(3) : String(val)}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Execution Controls & Instant Inference Metrics */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Pipeline Parameters Card */}
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Pipeline Controls</span>
              <Sliders size={18} color="var(--accent-teal)" />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {/* Confidence Threshold */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "6px" }}>
                  <span style={{ fontWeight: 600 }}>YOLO Confidence</span>
                  <span style={{ color: "var(--accent-teal)", fontWeight: 700 }}>{confidence}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  style={{ width: "100%", accentColor: "var(--accent-teal)" }}
                />
              </div>

              {/* Live Confidence Filter */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "6px" }}>
                  <span style={{ fontWeight: 600 }}>View Filter Cutoff</span>
                  <span style={{ color: "var(--text-secondary)", fontWeight: 700 }}>{minConfidenceFilter}</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.85"
                  step="0.05"
                  value={minConfidenceFilter}
                  onChange={(e) => setMinConfidenceFilter(parseFloat(e.target.value))}
                  style={{ width: "100%", accentColor: "#8B5CF6" }}
                />
              </div>

              {/* Toggles */}
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.88rem" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={tracking}
                    onChange={(e) => setTracking(e.target.checked)}
                    style={{ accentColor: "var(--accent-teal)" }}
                  />
                  <span>ByteTrack Persistent IDs</span>
                </label>

                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={attributes}
                    onChange={(e) => setAttributes(e.target.checked)}
                    style={{ accentColor: "var(--accent-teal)" }}
                  />
                  <span>Clothing / Appearance Attributes</span>
                </label>
              </div>

              {/* Run Trigger Button */}
              <button
                type="button"
                className="vl-btn vl-btn-primary"
                style={{ width: "100%", marginTop: "0.5rem" }}
                onClick={() => runAnalysis()}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw size={16} className="vl-pulse-dot" /> Computing Inference...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> Run Analysis Pipeline
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Summary Card */}
          {apiError ? (
            <div className="vl-card" role="alert" style={{ borderColor: "rgba(239,68,68,0.4)" }}>
              <div className="vl-card-header">
                <span className="vl-card-label">Backend Unreachable</span>
              </div>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                {apiError} Start the FastAPI service (`python start_local.py`) and retry.
              </p>
            </div>
          ) : result ? (
            <div className="vl-card">
              <div className="vl-card-header">
                <span className="vl-card-label">Inference Result</span>
                <span className={`vl-density-badge vl-density-${result.density_label}`}>
                  {result.density_label} DENSITY
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-tertiary)", textTransform: "uppercase" }}>
                    Detected Crowd Volume
                  </div>
                  <div style={{ fontSize: "2rem", fontWeight: 800, color: "#0F172A", lineHeight: 1.1 }}>
                    {filteredDetections.length}{" "}
                    <span style={{ fontSize: "0.9rem", color: "var(--text-tertiary)", fontWeight: 500 }}>
                      persons (total: {result.people_count})
                    </span>
                  </div>
                </div>

                {/* Probability Distribution */}
                <div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 600, marginBottom: "8px" }}>
                    Regime Probabilities
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {Object.entries(result.probabilities).map(([label, prob]) => (
                      <div key={label}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: "3px" }}>
                          <span style={{ fontWeight: 600 }}>{label}</span>
                          <span>{(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div style={{ height: "5px", background: "#F1F5F9", borderRadius: "4px", overflow: "hidden" }}>
                          <div
                            style={{
                              width: `${prob * 100}%`,
                              height: "100%",
                              background:
                                label === "LOW" ? "#10B981" : label === "MEDIUM" ? "#F59E0B" : "#EF4444",
                              borderRadius: "4px",
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ padding: "10px", background: "#F8FAFC", borderRadius: "8px", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                  <strong>Model Used:</strong> {result.model_name ?? "Random Forest Ensemble"}
                </div>
              </div>
            </div>
          ) : (
            <div className="vl-card" style={{ textAlign: "center", padding: "2.5rem 1.5rem" }}>
              <Info size={28} style={{ color: "var(--text-muted)", margin: "0 auto 10px" }} />
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-primary)" }}>
                Ready to Analyze
              </h4>
              <p style={{ color: "var(--text-tertiary)", fontSize: "0.84rem", marginTop: "4px" }}>
                Click &ldquo;Run Analysis Pipeline&rdquo; or upload a custom photograph to inspect real-time crowd dynamics.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
