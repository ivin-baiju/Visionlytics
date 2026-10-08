"use client";

import React from "react";
import { Eye, Shield, Cpu, Code2, Globe, ExternalLink, GitBranch } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="vl-main-content">
      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
          About Visionlytics Platform
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
          Production-grade computer vision and statistical machine learning architecture for intelligent crowd dynamics.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
        {/* Core Philosophy */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Design Philosophy</span>
            <Eye size={18} color="var(--accent-blue)" />
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", lineHeight: 1.6 }}>
            Traditional crowd analytics either count people naively without spatial context or rely on opaque deep learning density heatmaps that lack statistical validation.
            <br /><br />
            <strong>VISIONLYTICS</strong> solves this by using deep object detection (YOLOv8s) strictly as a sensory perception layer. It derives a calibrated 10-dimensional spatial descriptor vector and passes it into classical statistical classifiers. This achieves high accuracy with mathematical interpretability and zero data leakage.
          </p>
        </div>

        {/* Tech Stack */}
        <div className="vl-card">
          <div className="vl-card-header">
            <span className="vl-card-label">Engineering Stack</span>
            <Cpu size={18} color="var(--accent-purple)" />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "0.85rem" }}>
            <div style={{ padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
              <span style={{ color: "var(--text-tertiary)", fontSize: "0.75rem", display: "block" }}>Frontend</span>
              <strong>Next.js 16 + React</strong>
            </div>
            <div style={{ padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
              <span style={{ color: "var(--text-tertiary)", fontSize: "0.75rem", display: "block" }}>Backend Microservice</span>
              <strong>FastAPI + Python 3.10+</strong>
            </div>
            <div style={{ padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
              <span style={{ color: "var(--text-tertiary)", fontSize: "0.75rem", display: "block" }}>Computer Vision</span>
              <strong>Ultralytics YOLOv8s</strong>
            </div>
            <div style={{ padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
              <span style={{ color: "var(--text-tertiary)", fontSize: "0.75rem", display: "block" }}>Machine Learning</span>
              <strong>Scikit-Learn + PyTorch</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 10 Spatial Features Table */}
      <div className="vl-card" style={{ marginBottom: "2rem" }}>
        <div className="vl-card-header">
          <span className="vl-card-label">The 10 Spatial Descriptor Dimensions</span>
          <Code2 size={18} color="var(--accent-emerald)" />
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="vl-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Feature Key</th>
                <th>Mathematical Meaning</th>
                <th>Range</th>
                <th>Importance</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td><code>people_count</code></td>
                <td>Total count of detected individuals in frame</td>
                <td>[0, ∞)</td>
                <td>Primary volume metric</td>
              </tr>
              <tr>
                <td>2</td>
                <td><code>occupancy_ratio</code></td>
                <td>Sum of bounding box areas divided by frame area</td>
                <td>[0, 1]</td>
                <td>Perspective space consumption</td>
              </tr>
              <tr>
                <td>3</td>
                <td><code>avg_person_area</code></td>
                <td>Mean individual bounding box footprint</td>
                <td>[0, 1]</td>
                <td>Depth perspective scaling</td>
              </tr>
              <tr>
                <td>4</td>
                <td><code>avg_distance</code></td>
                <td>Pairwise Euclidean distance across all centroids</td>
                <td>[0, √2]</td>
                <td>Mean interpersonal spacing</td>
              </tr>
              <tr>
                <td>5</td>
                <td><code>min_distance</code></td>
                <td>Minimum distance between any two individuals</td>
                <td>[0, √2]</td>
                <td>Localized bottleneck clusters</td>
              </tr>
              <tr>
                <td>6</td>
                <td><code>std_distance</code></td>
                <td>Standard deviation of interpersonal distances</td>
                <td>[0, √2]</td>
                <td>Spatial uniformity / dispersion</td>
              </tr>
              <tr>
                <td>7</td>
                <td><code>top_region_count</code></td>
                <td>Persons detected in top 33% vertical zone</td>
                <td>[0, N]</td>
                <td>Background crowd depth</td>
              </tr>
              <tr>
                <td>8</td>
                <td><code>middle_region_count</code></td>
                <td>Persons detected in middle 33% vertical zone</td>
                <td>[0, N]</td>
                <td>Midground pedestrian activity</td>
              </tr>
              <tr>
                <td>9</td>
                <td><code>bottom_region_count</code></td>
                <td>Persons detected in bottom 33% vertical zone</td>
                <td>[0, N]</td>
                <td>Immediate camera foreground</td>
              </tr>
              <tr>
                <td>10</td>
                <td><code>density_ratio</code></td>
                <td>Ratio of high density clusters over free space</td>
                <td>[0, 1]</td>
                <td>Dynamic congestion index</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* GitHub & Links */}
      <div className="vl-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h4 style={{ fontSize: "1rem", fontWeight: 700 }}>Open Source Repository</h4>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "2px" }}>
            Source code, models, and deployment configurations are available on GitHub.
          </p>
        </div>
        <a
          href="https://github.com/ivin-baiju/Visionlytics"
          target="_blank"
          rel="noopener noreferrer"
          className="vl-btn vl-btn-secondary"
          style={{ textDecoration: "none" }}
        >
          <GitBranch size={16} /> GitHub Repository
        </a>
      </div>
    </div>
  );
}
