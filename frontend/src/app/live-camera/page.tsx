"use client";

import React, { useState, useRef, useEffect } from "react";
import { Camera, CameraOff, Video, Activity, Sparkles, RefreshCw } from "lucide-react";
import { analyzeFrameApi } from "@/lib/api";
import { FrameAnalysisResult } from "@/types";

export default function LiveCameraPage() {
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [fps, setFps] = useState<number>(0);
  const [result, setResult] = useState<FrameAnalysisResult | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startCamera = async () => {
    setErrorMsg(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsStreaming(true);
    } catch (err: any) {
      console.error(err);
      setErrorMsg("Camera access denied or unavailable. Check browser permissions.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsStreaming(false);
    setResult(null);
  };

  // Inference capture loop
  useEffect(() => {
    if (!isStreaming) return;

    let lastTime = performance.now();
    let frameCount = 0;

    intervalRef.current = setInterval(async () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas || video.readyState < 2) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Measure FPS
      frameCount++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frameCount);
        frameCount = 0;
        lastTime = now;
      }

      // Convert canvas snapshot to blob and send to backend
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        const res = await analyzeFrameApi(blob, 0.3, true, false);
        setResult(res);

        // Draw bounding boxes on canvas
        res.detections.forEach((det) => {
          const [x1, y1, x2, y2] = det.bbox;
          ctx.strokeStyle = "#38BDF8";
          ctx.lineWidth = 3;
          ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

          ctx.fillStyle = "rgba(16, 21, 34, 0.85)";
          ctx.fillRect(x1, Math.max(0, y1 - 20), 80, 18);
          ctx.fillStyle = "#38BDF8";
          ctx.font = "bold 11px Inter, sans-serif";
          ctx.fillText(`Person ${(det.confidence * 100).toFixed(0)}%`, x1 + 6, Math.max(12, y1 - 6));
        });
      }, "image/jpeg", 0.7);
    }, 800);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isStreaming]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="vl-main-content">
      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 800 }}>
          Real-Time Camera Surveillance
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginTop: "4px" }}>
          Live WebRTC camera streaming with real-time person bounding box detection and instantaneous density estimation.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.5rem" }}>
        {/* Left Column: Camera View */}
        <div className="vl-card" style={{ padding: "1.25rem" }}>
          <div style={{ position: "relative", borderRadius: "12px", overflow: "hidden", background: "#050810", minHeight: "420px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            {/* Hidden Video Source */}
            <video
              ref={videoRef}
              playsInline
              muted
              style={{ display: "none" }}
            />

            {/* Visual Canvas */}
            {isStreaming ? (
              <canvas
                ref={canvasRef}
                style={{ width: "100%", height: "auto", display: "block" }}
              />
            ) : (
              <div style={{ textAlign: "center", padding: "3rem" }}>
                <Camera size={48} color="var(--text-tertiary)" style={{ margin: "0 auto 12px" }} />
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600 }}>Camera Stream Disconnected</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "6px" }}>
                  Grant browser permissions to start live crowd detection.
                </p>
              </div>
            )}

            {/* Top HUD */}
            {isStreaming && (
              <div
                style={{
                  position: "absolute",
                  top: "14px",
                  left: "14px",
                  display: "flex",
                  gap: "10px",
                  zIndex: 10,
                }}
              >
                <span className="vl-badge live">
                  <span className="vl-pulse-dot" /> LIVE {fps} FPS
                </span>
                {result && (
                  <span className={`vl-density-badge vl-density-${result.density_label}`}>
                    {result.density_label} DENSITY
                  </span>
                )}
              </div>
            )}
          </div>

          {errorMsg && (
            <div style={{ color: "var(--accent-rose)", fontSize: "0.85rem", marginTop: "10px" }}>
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Action Button */}
          <div style={{ marginTop: "1.25rem" }}>
            {isStreaming ? (
              <button
                type="button"
                className="vl-btn vl-btn-secondary"
                onClick={stopCamera}
                style={{ width: "100%" }}
              >
                <CameraOff size={16} /> Disconnect Live Stream
              </button>
            ) : (
              <button
                type="button"
                className="vl-btn vl-btn-primary"
                onClick={startCamera}
                style={{ width: "100%" }}
              >
                <Video size={16} /> Connect Live Camera
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Live Detection Feed */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Live Scene Count</span>
              <Activity size={16} color="var(--accent-blue)" />
            </div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: "2.4rem", fontWeight: 800 }}>
              {result ? result.people_count : 0}
            </div>
            <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Detected persons in field of view
            </span>
          </div>

          <div className="vl-card">
            <div className="vl-card-header">
              <span className="vl-card-label">Confidence & Model</span>
              <Sparkles size={16} color="var(--accent-purple)" />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Detection Model:</span>
                <strong>YOLOv8s</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Mean Confidence:</span>
                <strong style={{ color: "var(--accent-emerald)" }}>
                  {result ? `${(result.confidence * 100).toFixed(0)}%` : "N/A"}
                </strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
