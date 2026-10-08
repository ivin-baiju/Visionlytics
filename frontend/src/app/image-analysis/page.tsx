"use client";

import React, { useState, useRef } from "react";
import { Upload, Sliders, RefreshCw, Sparkles, AlertCircle, Eye, Info } from "lucide-react";
import BoundingBoxCanvas from "@/components/BoundingBoxCanvas";
import { analyzeFrameApi } from "@/lib/api";
import { FrameAnalysisResult, DensityLabel } from "@/types";

// High quality sample crowd images (free unsplash samples)
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
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<FrameAnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setSelectedImage(url);
      runAnalysis(file);
    }
  };

  const runAnalysis = async (fileOrBlob?: Blob) => {
    setIsAnalyzing(true);
    try {
      let blob: Blob;
      if (fileOrBlob) {
        blob = fileOrBlob;
      } else {
        const res = await fetch(selectedImage);
        blob = await res.blob();
      }

      const data = await analyzeFrameApi(blob, confidence, tracking, attributes);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="vl-main-content">
      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
          Image Analysis Workspace
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
          Upload crowd photographs to run YOLOv8s person detection, spatial feature extraction, and density regime classification.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.5rem", alignItems: "start" }}>
        {/* Left Column: Image Canvas & Preview */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Main Visual Display */}
          <div className="vl-card" style={{ padding: "1.25rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Eye size={18} color="var(--accent-blue)" />
                <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>Perception Canvas</span>
              </div>
              {result && (
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    Count: <strong style={{ color: "#FFF" }}>{result.people_count}</strong>
                  </span>
                  <span className={`vl-density-badge vl-density-${result.density_label}`}>
                    {result.density_label} DENSITY
                  </span>
                </div>
              )}
            </div>

            <BoundingBoxCanvas
              imageSrc={selectedImage}
              detections={result?.detections || []}
              attributes={result?.attributes}
              showAttributes={attributes}
            />

            {/* Run Analysis Action Button */}
            <div style={{ display: "flex", gap: "12px", marginTop: "1rem" }}>
              <button
                type="button"
                className="vl-btn vl-btn-primary"
                style={{ flex: 1 }}
                onClick={() => runAnalysis()}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="vl-pulse-dot" size={16} /> Analyzing Frame...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> Run Full Detection Pipeline
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Sample Presets */}
          <div className="vl-card">
            <span className="vl-card-label" style={{ marginBottom: "0.75rem", display: "block" }}>
              Or Try A Curated Sample Image:
            </span>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
              {SAMPLES.map((s) => (
                <button
                  type="button"
                  key={s.name}
                  onClick={() => {
                    setSelectedImage(s.url);
                    setResult(null);
                  }}
                  className="vl-btn vl-btn-secondary"
                  style={{
                    fontSize: "0.75rem",
                    padding: "8px 10px",
                    borderColor: selectedImage === s.url ? "var(--accent-blue)" : undefined,
                  }}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Parameters & Analysis Results */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* File Upload Box */}
          <div
            className="vl-upload-box"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              style={{ display: "none" }}
            />
            <Upload size={32} color="var(--accent-blue)" style={{ margin: "0 auto 10px" }} />
            <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>Upload Crowd Photo</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginTop: "4px" }}>
              JPG, PNG, WebP up to 20MB
            </div>
          </div>

          {/* Hyperparameters Card */}
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Detection Settings</span>
              <Sliders size={16} color="var(--accent-blue)" />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginTop: "10px" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: "6px" }}>
                  <span>Confidence Threshold</span>
                  <strong style={{ color: "var(--accent-blue)" }}>{confidence.toFixed(2)}</strong>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  style={{ width: "100%", accentColor: "var(--accent-blue)" }}
                />
              </div>

              <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "0.85rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={tracking}
                  onChange={(e) => setTracking(e.target.checked)}
                  style={{ accentColor: "var(--accent-blue)", width: "16px", height: "16px" }}
                />
                <span>ByteTrack ID Assignment</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "0.85rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={attributes}
                  onChange={(e) => setAttributes(e.target.checked)}
                  style={{ accentColor: "var(--accent-blue)", width: "16px", height: "16px" }}
                />
                <span>Estimate Clothing & Hair Colors</span>
              </label>
            </div>
          </div>

          {/* Results Overview */}
          {result && (
            <div className="vl-card">
              <div className="vl-card-header">
                <span className="vl-card-label">Spatial Descriptors</span>
                <Info size={16} color="var(--accent-purple)" />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.82rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Occupancy Ratio:</span>
                  <strong>{(result.features.occupancy_ratio * 100).toFixed(1)}%</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Mean Spacing:</span>
                  <strong>{(result.features.avg_distance * 100).toFixed(1)}%</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Nearest Bottleneck:</span>
                  <strong>{(result.features.min_distance * 100).toFixed(1)}%</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-secondary)" }}>ML Classifier:</span>
                  <strong style={{ color: "var(--accent-blue)" }}>{result.model_name}</strong>
                </div>

                <div style={{ marginTop: "10px", paddingTop: "10px", borderTop: "1px solid var(--border-subtle)" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", display: "block", marginBottom: "6px" }}>
                    Calibrated Probabilities
                  </span>
                  {(["LOW", "MEDIUM", "HIGH"] as DensityLabel[]).map((label) => (
                    <div key={label} style={{ marginBottom: "6px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", marginBottom: "2px" }}>
                        <span>{label}</span>
                        <span>{((result.probabilities[label] || 0) * 100).toFixed(0)}%</span>
                      </div>
                      <div style={{ height: "4px", background: "rgba(255,255,255,0.06)", borderRadius: "2px" }}>
                        <div
                          style={{
                            width: `${(result.probabilities[label] || 0) * 100}%`,
                            height: "100%",
                            background: label === "LOW" ? "var(--accent-emerald)" : label === "MEDIUM" ? "var(--accent-amber)" : "var(--accent-rose)",
                            borderRadius: "2px",
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
