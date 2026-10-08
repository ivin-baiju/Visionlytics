"use client";

import React, { useEffect, useRef } from "react";
import { Detection, PersonAttribute } from "@/types";

interface BoundingBoxCanvasProps {
  imageSrc: string;
  detections: Detection[];
  attributes?: PersonAttribute[];
  showAttributes?: boolean;
}

export default function BoundingBoxCanvas({
  imageSrc,
  detections,
  attributes,
  showAttributes = false,
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

      // Draw base image
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Draw detections
      detections.forEach((det, idx) => {
        const [x1, y1, x2, y2] = det.bbox;
        const width = x2 - x1;
        const height = y2 - y1;

        // Bounding Box Glow
        ctx.save();
        ctx.strokeStyle = "#38BDF8";
        ctx.lineWidth = 2.5;
        ctx.shadowColor = "rgba(56, 189, 248, 0.7)";
        ctx.shadowBlur = 8;
        ctx.strokeRect(x1, y1, width, height);

        // Semi-transparent box fill
        ctx.fillStyle = "rgba(56, 189, 248, 0.12)";
        ctx.fillRect(x1, y1, width, height);
        ctx.restore();

        // Label Badge
        const personId = det.person_id ? `ID #${det.person_id}` : `Person ${(det.confidence * 100).toFixed(0)}%`;
        const attr = attributes && attributes[idx];
        const labelText = showAttributes && attr 
          ? `${personId} • ${attr.clothing_color}`
          : personId;

        ctx.font = "bold 12px Inter, sans-serif";
        const textWidth = ctx.measureText(labelText).width;

        // Label background badge
        ctx.fillStyle = "rgba(16, 21, 34, 0.9)";
        ctx.fillRect(x1, Math.max(0, y1 - 22), textWidth + 14, 20);

        // Accent border on top of label
        ctx.fillStyle = "#38BDF8";
        ctx.fillRect(x1, Math.max(0, y1 - 22), 3, 20);

        // Label text
        ctx.fillStyle = "#F8FAFC";
        ctx.fillText(labelText, x1 + 8, Math.max(14, y1 - 8));

        // Centroid point
        const cx = x1 + width / 2;
        const cy = y1 + height / 2;
        ctx.beginPath();
        ctx.arc(cx, cy, 3, 0, 2 * Math.PI);
        ctx.fillStyle = "#10B981";
        ctx.fill();
      });
    };
  }, [imageSrc, detections, attributes, showAttributes]);

  return (
    <div className="vl-canvas-wrap">
      <canvas ref={canvasRef} style={{ width: "100%", height: "auto" }} />
    </div>
  );
}
