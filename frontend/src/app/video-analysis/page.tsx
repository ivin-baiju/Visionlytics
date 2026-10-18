"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { Play, Pause, Upload, Film, Activity, TrendingUp, AlertTriangle } from "lucide-react";
import { analyzeFrameApi } from "@/lib/api";
import { useGuestQuota } from "@/lib/useGuestQuota";
import GuestLimitBanner from "@/components/GuestLimitBanner";
import { FrameAnalysisResult } from "@/types";

export default function VideoAnalysisPage() {
  const { isGuest, remaining, limit, isLimitReached, incrementUsage } = useGuestQuota();
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [videoSrc, setVideoSrc] = useState<string>("/bg_video.mp4");
  const [currentCount, setCurrentCount] = useState<number>(0);
  const [densityLabel, setDensityLabel] = useState<string>("LOW");
  const [history, setHistory] = useState<{ time: string; count: number }[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const captureRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastUpdateRef = useRef<number>(0);
  const inFlightRef = useRef<boolean>(false);
  const prevVideoUrl = useRef<string | null>(null);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      if (isLimitReached) {
        setApiError("Guest limit reached! Register with your email/phone to enjoy unlimited video analysis.");
        return;
      }
      incrementUsage();
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (isLimitReached) {
      setApiError("Guest upload limit of 10 reached. Please log in or register for unlimited uploads.");
      return;
    }
    const file = e.target.files?.[0];
    if (file) {
      const allowed = incrementUsage();
      if (!allowed) {
        setApiError("Guest limit reached! Register with your email or phone to enjoy unlimited video uploads.");
        return;
      }
      // Clean up previous object URL
      if (prevVideoUrl.current) {
        URL.revokeObjectURL(prevVideoUrl.current);
      }
      const url = URL.createObjectURL(file);
      prevVideoUrl.current = url;
      setVideoSrc(url);
      setIsPlaying(false);
    }
  };

  // Video frame extraction — real backend inference at ~2fps (500ms throttle).
  // Skips while a request is in flight so slow backends can't pile up.
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    if (!captureRef.current) captureRef.current = document.createElement("canvas");
    const capture = captureRef.current;

    const processFrame = (timestamp: number) => {
      if (!video.paused && !video.ended) {
        // Throttle to ~2 inference calls per second to protect the backend.
        if (timestamp - lastUpdateRef.current >= 500 && !inFlightRef.current) {
          lastUpdateRef.current = timestamp;

          const ctx = canvas.getContext("2d");
          if (ctx) {
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 360;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          }
          // Snapshot to an offscreen canvas so overlays never feed back in.
          capture.width = video.videoWidth || 640;
          capture.height = video.videoHeight || 360;
          const capCtx = capture.getContext("2d");
          if (capCtx) {
            capCtx.drawImage(video, 0, 0, capture.width, capture.height);
            inFlightRef.current = true;
            setIsAnalyzing(true);
            capture.toBlob(async (blob) => {
              try {
                if (!blob) return;
                const res: FrameAnalysisResult = await analyzeFrameApi(blob, 0.3, false, false);
                setCurrentCount(res.people_count);
                setDensityLabel(res.density_label);
                setApiError(null);
                setHistory((prev) => {
                  const now = new Date().toLocaleTimeString().slice(-5);
                  return [...prev.slice(-29), { time: now, count: res.people_count }];
                });
              } catch (err) {
                setApiError(err instanceof Error ? err.message : "Video inference failed");
              } finally {
                inFlightRef.current = false;
                setIsAnalyzing(false);
              }
            }, "image/jpeg", 0.8);
          }
        }
      }
      animationFrameRef.current = requestAnimationFrame(processFrame);
    };

    animationFrameRef.current = requestAnimationFrame(processFrame);
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isPlaying]);

  // Clean up object URL on unmount
  useEffect(() => {
    return () => {
      if (prevVideoUrl.current) {
        URL.revokeObjectURL(prevVideoUrl.current);
      }
    };
  }, []);

  return (
    <div className="vl-container">
      {/* Guest Quota Banner */}
      {isGuest && (
        <GuestLimitBanner
          remaining={remaining}
          limit={limit}
          isLimitReached={isLimitReached}
          featureName="video surveillance uploads and inference"
        />
      )}

      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
          Video Surveillance Analytics
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
          Continuous frame-by-frame crowd monitoring with temporal flow tracking and persistent trajectory estimation.
        </p>
      </div>

      <div className="vl-responsive-grid-sidebar">
        {apiError && (
          <div role="alert" className="vl-card" style={{ borderColor: "rgba(239,68,68,0.4)", gridColumn: "1 / -1" }}>
            <span style={{ fontSize: "0.85rem", color: "#DC2626", fontWeight: 600 }}>
              Backend unreachable: {apiError}. Start it with `python start_local.py` — video shows preview only until then.
              {isAnalyzing ? " (retrying…)" : ""}
            </span>
          </div>
        )}
        {/* Left Column: Player & Stream */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div className="vl-card" style={{ padding: "1.25rem" }}>
            <div style={{ position: "relative", borderRadius: "12px", overflow: "hidden", background: "#000" }}>
              <video
                ref={videoRef}
                src={videoSrc}
                loop
                playsInline
                muted
                style={{ width: "100%", height: "auto", display: "block" }}
              />
              <canvas ref={canvasRef} style={{ display: "none" }} />

              {/* Floating Live Overlay HUD */}
              <div
                style={{
                  position: "absolute",
                  top: "14px",
                  left: "14px",
                  display: "flex",
                  gap: "10px",
                  zIndex: 10,
                  flexWrap: "wrap",
                }}
              >
                {isPlaying && (
                  <span className="vl-badge live">
                    <span className="vl-pulse-dot" /> STREAM ACTIVE
                  </span>
                )}
                <span className={`vl-density-badge vl-density-${densityLabel}`}>
                  {densityLabel} DENSITY
                </span>
              </div>
            </div>

            {/* Playback Controls */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "1rem", flexWrap: "wrap", gap: "10px" }}>
              <button
                type="button"
                className="vl-btn vl-btn-primary"
                onClick={togglePlay}
                style={{ minWidth: "130px" }}
              >
                {isPlaying ? (
                  <>
                    <Pause size={16} /> Pause Feed
                  </>
                ) : (
                  <>
                    <Play size={16} /> Play Feed
                  </>
                )}
              </button>

              <label className="vl-btn vl-btn-secondary" style={{ cursor: "pointer" }}>
                <Upload size={16} /> Upload Video
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleVideoUpload}
                  style={{ display: "none" }}
                />
              </label>
            </div>
          </div>

          {/* Temporal Graph Over Time */}
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Temporal Crowd Volume (Recent Frames)</span>
              <TrendingUp size={16} color="var(--accent-blue)" />
            </div>
            <div style={{ display: "flex", alignItems: "flex-end", height: "120px", gap: "8px", paddingTop: "10px" }}>
              {history.length === 0 ? (
                <div style={{ width: "100%", textAlign: "center", color: "var(--text-tertiary)", fontSize: "0.82rem", alignSelf: "center" }}>
                  Press Play to start collecting temporal data
                </div>
              ) : (
                history.map((h, i) => {
                  const heightPct = Math.min(100, (h.count / 15) * 100);
                  return (
                    <div
                      key={i}
                      style={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        height: "100%",
                        justifyContent: "flex-end",
                      }}
                    >
                      <span style={{ fontSize: "0.65rem", color: "var(--text-tertiary)", marginBottom: "4px" }}>
                        {h.count}
                      </span>
                      <div
                        style={{
                          width: "100%",
                          height: `${heightPct}%`,
                          background:
                            h.count > 10
                              ? "var(--accent-rose)"
                              : h.count > 5
                              ? "var(--accent-amber)"
                              : "var(--accent-emerald)",
                          borderRadius: "4px 4px 0 0",
                          transition: "height 0.3s ease",
                        }}
                      />
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Live Stream Metrics */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Live Metrics</span>
              <Activity size={16} color="var(--accent-emerald)" />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <span style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>Current People In View</span>
                <div className="vl-kpi-value" style={{ fontSize: "2.4rem" }}>
                  {currentCount}
                </div>
              </div>
              <div>
                <span style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>Surveillance Status</span>
                <div style={{
                  color: currentCount > 10 ? "var(--accent-rose)" : "var(--accent-emerald)",
                  fontWeight: 600,
                  fontSize: "0.9rem",
                }}>
                  {currentCount > 10 ? "⚠ High Congestion Detected" : "Normal Pedestrian Flow"}
                </div>
              </div>
            </div>
          </div>

          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Safety Alerts</span>
              <AlertTriangle size={16} color="var(--accent-amber)" />
            </div>
            <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
              {currentCount > 10 ? (
                <div className="vl-alert-danger vl-fade-in">
                  <AlertTriangle size={16} />
                  <span>High congestion bottleneck detected in center zone. Consider activating overflow routing.</span>
                </div>
              ) : (
                <span>No safety thresholds exceeded. Density within operational safety parameters.</span>
              )}
            </div>
          </div>

          {/* Detection Summary */}
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Session Summary</span>
              <Film size={16} color="var(--accent-indigo)" />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.82rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Frames Processed:</span>
                <strong>{history.length}</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Peak Count:</span>
                <strong style={{ color: "var(--accent-amber)" }}>
                  {history.length > 0 ? Math.max(...history.map(h => h.count)) : 0}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Avg Count:</span>
                <strong>
                  {history.length > 0
                    ? (history.reduce((sum, h) => sum + h.count, 0) / history.length).toFixed(1)
                    : "0"}
                </strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
