"use client";

import React, { useEffect, useRef } from "react";
import { Detection, PersonAttribute } from "@/types";

interface BoundingBoxCanvasProps {
  imageSrc: string;
  detections: Detection[];
  attributes?: PersonAttribute[];
  showAttributes?: boolean;
  showHeatmap?: boolean;
  showCentroids?: boolean;
  showBoxes?: boolean;
}

export default function BoundingBoxCanvas({
  imageSrc,
  detections,
  attributes,
  showAttributes = false,
  showHeatmap = false,
  showCentroids = true,
  showBoxes = true,
}: BoundingBoxCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageSrc) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageSrc;

    img.onload = () => {
      canvas.width = img.naturalWidth || 640;
      canvas.height = img.naturalHeight || 480;

      // 1. Draw base frame
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // 2. Spatial Density Heatmap Overlay
      if (showHeatmap && detections.length > 0) {
        const heatCanvas = document.createElement("canvas");
        heatCanvas.width = canvas.width;
        heatCanvas.height = canvas.height;
        const heatCtx = heatCanvas.getContext("2d");

        if (heatCtx) {
          detections.forEach((det) => {
            const [x1, y1, x2, y2] = det.bbox;
            const cx = (x1 + x2) / 2;
            const cy = (y1 + y2) / 2;
            const radius = Math.max(35, Math.min(100, Math.sqrt((x2 - x1) * (y2 - y1)) * 0.9));

            const grad = heatCtx.createRadialGradient(cx, cy, 0, cx, cy, radius);
            grad.addColorStop(0, "rgba(239, 68, 68, 0.45)");
            grad.addColorStop(0.4, "rgba(245, 158, 11, 0.3)");
            grad.addColorStop(0.8, "rgba(16, 185, 129, 0.15)");
            grad.addColorStop(1, "rgba(16, 185, 129, 0)");

            heatCtx.fillStyle = grad;
            heatCtx.beginPath();
            heatCtx.arc(cx, cy, radius, 0, 2 * Math.PI);
            heatCtx.fill();
          });

          ctx.save();
          ctx.globalAlpha = 0.85;
          ctx.drawImage(heatCanvas, 0, 0);
          ctx.restore();
        }
      }

      // 3. Draw Bounding Boxes and Labels
      detections.forEach((det, idx) => {
        const [x1, y1, x2, y2] = det.bbox;
        const width = x2 - x1;
        const height = y2 - y1;
        const cx = x1 + width / 2;
        const cy = y1 + height / 2;

        if (showBoxes) {
          ctx.save();
          ctx.strokeStyle = "#0D9488";
          ctx.lineWidth = 2.2;
          ctx.strokeRect(x1, y1, width, height);

          // Subtle box highlight
          ctx.fillStyle = "rgba(13, 148, 136, 0.08)";
          ctx.fillRect(x1, y1, width, height);
          ctx.restore();

          // Label Badge
          const personId = det.person_id ? `ID #${det.person_id}` : `Person ${(det.confidence * 100).toFixed(0)}%`;
          const attr = attributes && attributes[idx];
          const labelText = showAttributes && attr 
            ? `${personId} • ${attr.clothing_color}`
            : personId;

          ctx.font = "600 11px Inter, sans-serif";
          const textWidth = ctx.measureText(labelText).width;

          // Label background pill
          ctx.fillStyle = "#0F172A";
          ctx.beginPath();
          ctx.roundRect(x1, Math.max(0, y1 - 22), textWidth + 14, 20, 4);
          ctx.fill();

          // Accent color pip
          ctx.fillStyle = "#0D9488";
          ctx.fillRect(x1, Math.max(0, y1 - 22), 3, 20);

          // Label text
          ctx.fillStyle = "#FFFFFF";
          ctx.fillText(labelText, x1 + 8, Math.max(14, y1 - 8));
        }

        // 4. Centroid dot
        if (showCentroids) {
          ctx.beginPath();
          ctx.arc(cx, cy, 3.5, 0, 2 * Math.PI);
          ctx.fillStyle = "#EF4444";
          ctx.fill();
          ctx.strokeStyle = "#FFFFFF";
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      });
    };
  }, [imageSrc, detections, attributes, showAttributes, showHeatmap, showCentroids, showBoxes]);

  return (
    <div className="vl-canvas-wrap">
      <canvas ref={canvasRef} style={{ width: "100%", height: "auto" }} />
    </div>
  );
}
