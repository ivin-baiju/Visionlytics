export interface Point2D {
  x: number;
  y: number;
}

/**
 * Ray-casting point-in-polygon check for normalized coordinates [0, 1].
 */
export function pointInPolygon(pt: Point2D, polygon: Point2D[]): boolean {
  if (polygon.length < 3) return false;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i]!.x;
    const yi = polygon[i]!.y;
    const xj = polygon[j]!.x;
    const yj = polygon[j]!.y;
    const intersect =
      yi > pt.y !== yj > pt.y &&
      pt.x < ((xj - xi) * (pt.y - yi)) / (yj - yi + 1e-12) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

/**
 * Computes signed side of directed line A -> B for point P.
 * Transitions from >0 to <0 or <0 to >0 across frames indicate line crossings (in/out).
 */
export function lineSide(a: Point2D, b: Point2D, p: Point2D): number {
  return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
}

export interface ZoneDefinition {
  id: string;
  name: string;
  kind: "polygon" | "line";
  points: Point2D[];
}

export interface FrameDetectionForZones {
  trackId: number;
  label: string;
  confidence: number;
  uncertain: boolean;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  colours: Array<{ name: string; hex: string; share: number }>;
  trajectory?: Array<{ frame: number; cx: number; cy: number }>;
}

export interface ZoneEvaluationSummary {
  zoneId: string;
  zoneName: string;
  kind: "polygon" | "line";
  occupancyCount: number;
  occupantTrackIds: number[];
  lineInCount: number;
  lineOutCount: number;
}

export function evaluateZonesForFrame(
  zones: ZoneDefinition[],
  detections: FrameDetectionForZones[],
  frameWidth: number,
  frameHeight: number,
): Record<string, ZoneEvaluationSummary> {
  const out: Record<string, ZoneEvaluationSummary> = {};
  const w = Math.max(1, frameWidth);
  const h = Math.max(1, frameHeight);

  for (const z of zones) {
    const summary: ZoneEvaluationSummary = {
      zoneId: z.id,
      zoneName: z.name,
      kind: z.kind,
      occupancyCount: 0,
      occupantTrackIds: [],
      lineInCount: 0,
      lineOutCount: 0,
    };

    for (const d of detections) {
      if (d.uncertain) continue;
      // Foot point (bottom-center of bounding box) in normalized coordinates
      const foot: Point2D = {
        x: (0.5 * (d.bbox.x1 + d.bbox.x2)) / w,
        y: d.bbox.y2 / h,
      };
      if (z.kind === "polygon" && z.points.length >= 3) {
        if (pointInPolygon(foot, z.points)) {
          summary.occupancyCount += 1;
          summary.occupantTrackIds.push(d.trackId);
        }
      } else if (z.kind === "line" && z.points.length >= 2) {
        const a = z.points[0]!;
        const b = z.points[1]!;
        const traj = d.trajectory ?? [];
        if (traj.length >= 2) {
          const prev = traj[traj.length - 2]!;
          const curr = traj[traj.length - 1]!;
          const sPrev = lineSide(a, b, { x: prev.cx / w, y: prev.cy / h });
          const sCurr = lineSide(a, b, { x: curr.cx / w, y: curr.cy / h });
          if (sPrev < 0 && sCurr >= 0) summary.lineInCount += 1;
          else if (sPrev > 0 && sCurr <= 0) summary.lineOutCount += 1;
        }
      }
    }

    out[z.id] = summary;
  }

  return out;
}
