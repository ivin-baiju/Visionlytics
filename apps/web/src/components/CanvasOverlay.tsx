import { useEffect, useRef } from "react";

export interface Swatch {
  name: string;
  hex: string;
  share: number;
}

export interface DetectionItem {
  trackId: number;
  label: string;
  confidence: number;
  uncertain: boolean;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  colours: Swatch[];
  upperClothingColours?: Swatch[];
  lowerClothingColours?: Swatch[];
  trajectory?: Array<{ frame: number; cx: number; cy: number }>;
}

export interface ZoneOverlay {
  id: string;
  name: string;
  kind: "polygon" | "line";
  points: Array<{ x: number; y: number }>;
  colourHex: string;
}

export interface CanvasOverlayProps {
  imageDataUrl: string | null;
  naturalWidth: number;
  naturalHeight: number;
  detections: DetectionItem[];
  zones?: ZoneOverlay[];
  showHeatmap?: boolean;
  privacyBlur?: boolean;
  highlightedTrackId?: number | null;
  onCanvasPointClick?: (normX: number, normY: number) => void;
}

export function CanvasOverlay({
  imageDataUrl,
  naturalWidth,
  naturalHeight,
  detections,
  zones = [],
  showHeatmap = false,
  privacyBlur = false,
  highlightedTrackId = null,
  onCanvasPointClick,
}: CanvasOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const w = Math.max(320, naturalWidth || 960);
    const h = Math.max(240, naturalHeight || 540);
    canvas.width = w;
    canvas.height = h;

    const drawOverlays = () => {
      // 1. Optional crowd density heatmap
      if (showHeatmap) {
        for (const d of detections) {
          if (d.label !== "person") continue;
          const cx = 0.5 * (d.bbox.x1 + d.bbox.x2);
          const cy = 0.5 * (d.bbox.y1 + d.bbox.y2);
          const radius = Math.max(48, 0.35 * (d.bbox.y2 - d.bbox.y1));
          const grad = ctx.createRadialGradient(cx, cy, 4, cx, cy, radius);
          grad.addColorStop(0, "rgba(255, 178, 31, 0.48)");
          grad.addColorStop(0.5, "rgba(255, 107, 98, 0.22)");
          grad.addColorStop(1, "rgba(11, 12, 13, 0)");
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // 2. Polygon zones & counting lines
      for (const z of zones) {
        if (z.points.length < 2) continue;
        ctx.save();
        ctx.strokeStyle = z.colourHex;
        ctx.lineWidth = 2;
        ctx.beginPath();
        z.points.forEach((pt, idx) => {
          const px = pt.x * w;
          const py = pt.y * h;
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        if (z.kind === "polygon") {
          ctx.closePath();
          ctx.fillStyle = `${z.colourHex}22`;
          ctx.fill();
        }
        ctx.stroke();
        const first = z.points[0]!;
        ctx.fillStyle = "#0b0c0d";
        ctx.fillRect(first.x * w, first.y * h - 20, z.name.length * 7.5 + 12, 18);
        ctx.fillStyle = z.colourHex;
        ctx.font = "600 11px 'Geist Mono Variable', monospace";
        ctx.fillText(z.name, first.x * w + 6, first.y * h - 7);
        ctx.restore();
      }

      // 3. Bounding boxes, crop-mark reticles, privacy blur, trajectories, and labels
      for (const d of detections) {
        const { x1, y1, x2, y2 } = d.bbox;
        const bw = Math.max(4, x2 - x1);
        const bh = Math.max(4, y2 - y1);
        const isHighlighted = highlightedTrackId === d.trackId;
        const primaryHex = d.uncertain ? "#f0c24b" : isHighlighted ? "#5fd39a" : "#ffb21f";

        // Optional privacy head/plate redaction
        if (privacyBlur && d.label === "person") {
          const headH = Math.min(bh * 0.22, 64);
          ctx.save();
          ctx.fillStyle = "rgba(17, 19, 21, 0.92)";
          ctx.fillRect(x1 + bw * 0.18, y1 + 2, bw * 0.64, headH);
          ctx.strokeStyle = "#353a3f";
          ctx.strokeRect(x1 + bw * 0.18, y1 + 2, bw * 0.64, headH);
          ctx.restore();
        }

        // Trajectory trail
        if (d.trajectory && d.trajectory.length > 1) {
          ctx.save();
          ctx.strokeStyle = primaryHex;
          ctx.lineWidth = 2;
          ctx.beginPath();
          d.trajectory.forEach((pt, idx) => {
            if (idx === 0) ctx.moveTo(pt.cx, pt.cy);
            else ctx.lineTo(pt.cx, pt.cy);
          });
          ctx.stroke();
          ctx.restore();
        }

        // Outer hairline box (dashed when uncertain)
        ctx.save();
        ctx.strokeStyle = primaryHex;
        ctx.lineWidth = isHighlighted ? 2.5 : 1.25;
        if (d.uncertain) {
          ctx.setLineDash([5, 4]);
        }
        ctx.strokeRect(x1, y1, bw, bh);
        ctx.restore();

        // Precision corner reticles
        const tick = Math.min(12, bw * 0.25, bh * 0.25);
        ctx.save();
        ctx.strokeStyle = primaryHex;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        // Top-left
        ctx.moveTo(x1, y1 + tick);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x1 + tick, y1);
        // Top-right
        ctx.moveTo(x2 - tick, y1);
        ctx.lineTo(x2, y1);
        ctx.lineTo(x2, y1 + tick);
        // Bottom-left
        ctx.moveTo(x1, y2 - tick);
        ctx.lineTo(x1, y2);
        ctx.lineTo(x1 + tick, y2);
        // Bottom-right
        ctx.moveTo(x2 - tick, y2);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x2, y2 - tick);
        ctx.stroke();
        ctx.restore();

        // Telemetry tag pill above box
        const topColour = d.colours[0];
        const tagText = `#${d.trackId} ${d.label}${d.uncertain ? " [uncertain]" : ""} ${(d.confidence * 100).toFixed(0)}%${topColour ? ` · ${topColour.name}` : ""}`;
        ctx.save();
        ctx.font = "500 12px 'Geist Mono Variable', monospace";
        const textWidth = ctx.measureText(tagText).width;
        const pillW = textWidth + (topColour ? 22 : 12);
        const pillH = 20;
        const pillY = Math.max(0, y1 - pillH - 2);

        ctx.fillStyle = "rgba(11, 12, 13, 0.88)";
        ctx.fillRect(x1, pillY, pillW, pillH);
        ctx.strokeStyle = primaryHex;
        ctx.lineWidth = 1;
        ctx.strokeRect(x1, pillY, pillW, pillH);

        let textX = x1 + 6;
        if (topColour) {
          ctx.fillStyle = topColour.hex;
          ctx.fillRect(x1 + 5, pillY + 5, 10, 10);
          textX = x1 + 19;
        }
        ctx.fillStyle = "#ede8de";
        ctx.fillText(tagText, textX, pillY + 14);
        ctx.restore();
      }
    };

    if (!imageDataUrl) {
      ctx.fillStyle = "#111315";
      ctx.fillRect(0, 0, w, h);
      drawOverlays();
      return;
    }

    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, w, h);
      ctx.drawImage(img, 0, 0, w, h);
      drawOverlays();
    };
    img.src = imageDataUrl;
  }, [
    imageDataUrl,
    naturalWidth,
    naturalHeight,
    detections,
    zones,
    showHeatmap,
    privacyBlur,
    highlightedTrackId,
  ]);

  return (
    <div className="relative overflow-hidden border border-hairline bg-bg">
      <canvas
        ref={canvasRef}
        onClick={(e) => {
          if (!onCanvasPointClick || !canvasRef.current) return;
          const rect = canvasRef.current.getBoundingClientRect();
          const nx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
          const ny = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
          onCanvasPointClick(Number(nx.toFixed(4)), Number(ny.toFixed(4)));
        }}
        className="block max-h-[560px] w-full object-contain"
        aria-label="Annotated computer vision frame canvas"
      />
    </div>
  );
}
