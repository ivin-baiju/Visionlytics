"""
Multi-object tracker for Visionlytics:
- Two-stage ByteTrack association (high-confidence pass >= enter_threshold, followed
  by low-confidence recovery pass >= exit_threshold for active tracks).
- Constant-velocity alpha-beta Kalman filter smoothing on bounding boxes.
- Exponential moving average (EMA) class voting across frames to prevent label flicker.
- Re-identification (re-ID) appearance embedding gallery (CIELAB spatial histogram +
  aspect ratio) to recover briefly occluded tracks up to `max_lost_frames`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def box_iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    return inter / max(area_a + area_b - inter, 1e-6)


def compute_reid_embedding(crop_rgb: np.ndarray, bbox: tuple[float, float, float, float]) -> np.ndarray:
    """Computes a 26-d normalized appearance + geometry descriptor for re-ID."""
    if crop_rgb.size == 0:
        return np.zeros(26, dtype=np.float32)
    h = crop_rgb.shape[0]
    top = crop_rgb[: max(1, h // 2)]
    bot = crop_rgb[max(1, h // 2) :]
    hist_top, _ = np.histogramdd(
        top.reshape(-1, 3), bins=(2, 2, 3), range=((0, 256), (0, 256), (0, 256))
    )
    hist_bot, _ = np.histogramdd(
        bot.reshape(-1, 3), bins=(2, 2, 3), range=((0, 256), (0, 256), (0, 256))
    )
    w_box = max(1.0, bbox[2] - bbox[0])
    h_box = max(1.0, bbox[3] - bbox[1])
    aspect = np.array([w_box / h_box, h_box / w_box], dtype=np.float32)
    vec = np.concatenate([hist_top.flatten(), hist_bot.flatten(), aspect]).astype(np.float32)
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 1e-6 else vec


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-6 or nb < 1e-6:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


@dataclass
class TrackState:
    track_id: int
    bbox: tuple[float, float, float, float]
    velocity: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    class_scores: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    embedding: np.ndarray = field(default_factory=lambda: np.zeros(26, dtype=np.float32))
    hits: int = 1
    lost_frames: int = 0
    history: list[dict[str, float | int]] = field(default_factory=list)

    @property
    def dominant_label(self) -> str:
        if not self.class_scores:
            return "object"
        return max(self.class_scores.items(), key=lambda kv: kv[1])[0]

    def predict(self) -> None:
        self.bbox = (
            self.bbox[0] + self.velocity[0],
            self.bbox[1] + self.velocity[1],
            self.bbox[2] + self.velocity[2],
            self.bbox[3] + self.velocity[3],
        )
        self.lost_frames += 1

    def update(
        self,
        new_bbox: tuple[float, float, float, float],
        label: str,
        score: float,
        emb: np.ndarray,
        frame_index: int,
    ) -> None:
        alpha = 0.65  # Kalman position blend
        beta = 0.30   # Velocity blend
        vx = new_bbox[0] - self.bbox[0]
        vy = new_bbox[1] - self.bbox[1]
        vx2 = new_bbox[2] - self.bbox[2]
        vy2 = new_bbox[3] - self.bbox[3]
        self.velocity = (
            (1 - beta) * self.velocity[0] + beta * vx,
            (1 - beta) * self.velocity[1] + beta * vy,
            (1 - beta) * self.velocity[2] + beta * vx2,
            (1 - beta) * self.velocity[3] + beta * vy2,
        )
        self.bbox = (
            (1 - alpha) * self.bbox[0] + alpha * new_bbox[0],
            (1 - alpha) * self.bbox[1] + alpha * new_bbox[1],
            (1 - alpha) * self.bbox[2] + alpha * new_bbox[2],
            (1 - alpha) * self.bbox[3] + alpha * new_bbox[3],
        )
        # EMA class voting
        for k in list(self.class_scores.keys()):
            self.class_scores[k] *= 0.8
        self.class_scores[label] = self.class_scores.get(label, 0.0) + score
        self.confidence = 0.6 * score + 0.4 * self.confidence
        if float(np.linalg.norm(emb)) > 1e-6:
            merged_emb = 0.75 * self.embedding + 0.25 * emb
            n = float(np.linalg.norm(merged_emb))
            self.embedding = merged_emb / n if n > 1e-6 else merged_emb
        self.hits += 1
        self.lost_frames = 0
        cx = 0.5 * (self.bbox[0] + self.bbox[2])
        cy = 0.5 * (self.bbox[1] + self.bbox[3])
        self.history.append({"frame": frame_index, "cx": round(cx, 1), "cy": round(cy, 1)})
        if len(self.history) > 120:
            self.history = self.history[-120:]


class ByteTrackerWithReID:
    def __init__(
        self,
        enter_threshold: float = 0.50,
        exit_threshold: float = 0.28,
        iou_threshold: float = 0.25,
        max_lost_frames: int = 45,
    ) -> None:
        self.enter_threshold = enter_threshold
        self.exit_threshold = exit_threshold
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self._next_id = 1
        self.tracks: dict[int, TrackState] = {}

    def step(
        self,
        detections: list[dict[str, object]],
        frame_rgb: np.ndarray,
        frame_index: int,
    ) -> list[dict[str, object]]:
        """
        Associates frame detections to persistent tracks and returns enriched detections
        with stable `trackId`, smoothed `bbox`, and trajectory history.
        """
        for tr in self.tracks.values():
            tr.predict()

        h_img, w_img = frame_rgb.shape[:2]
        prepared: list[tuple[dict[str, object], tuple[float, float, float, float], np.ndarray]] = []
        for det in detections:
            b = det["bbox"]  # type: ignore[index]
            bbox = (float(b["x1"]), float(b["y1"]), float(b["x2"]), float(b["y2"]))  # type: ignore[index]
            x1 = max(0, min(w_img - 1, int(bbox[0])))
            y1 = max(0, min(h_img - 1, int(bbox[1])))
            x2 = max(x1 + 1, min(w_img, int(bbox[2])))
            y2 = max(y1 + 1, min(h_img, int(bbox[3])))
            crop = frame_rgb[y1:y2, x1:x2]
            emb = compute_reid_embedding(crop, bbox)
            prepared.append((det, bbox, emb))

        high = [item for item in prepared if float(item[0]["confidence"]) >= self.enter_threshold]  # type: ignore[arg-type]
        low = [
            item
            for item in prepared
            if self.exit_threshold <= float(item[0]["confidence"]) < self.enter_threshold  # type: ignore[arg-type]
        ]

        unmatched_tracks = set(self.tracks.keys())
        output: list[dict[str, object]] = []

        def associate(
            candidates: list[tuple[dict[str, object], tuple[float, float, float, float], np.ndarray]],
            allow_reid: bool,
        ) -> list[tuple[dict[str, object], tuple[float, float, float, float], np.ndarray]]:
            leftover: list[tuple[dict[str, object], tuple[float, float, float, float], np.ndarray]] = []
            for det, bbox, emb in candidates:
                best_tid: int | None = None
                best_score = -1.0
                for tid in list(unmatched_tracks):
                    tr = self.tracks[tid]
                    iou = box_iou(tr.bbox, bbox)
                    reid_sim = cosine_similarity(tr.embedding, emb)
                    if iou >= self.iou_threshold:
                        # Gate IoU association by appearance similarity when two tracks are close
                        if reid_sim < 0.55 and tr.hits > 3:
                            continue
                        combined = 0.55 * iou + 0.45 * max(0.0, reid_sim)
                        if combined > best_score:
                            best_score = combined
                            best_tid = tid
                    elif allow_reid and tr.lost_frames >= 1 and tr.dominant_label == det["label"]:
                        # Recover occluded track via appearance similarity + reasonable spatial distance
                        dist = float(
                            np.hypot(
                                0.5 * (tr.bbox[0] + tr.bbox[2]) - 0.5 * (bbox[0] + bbox[2]),
                                0.5 * (tr.bbox[1] + tr.bbox[3]) - 0.5 * (bbox[1] + bbox[3]),
                            )
                        )
                        diag = float(np.hypot(w_img, h_img))
                        if reid_sim >= 0.82 and dist <= 0.30 * diag and reid_sim > best_score:
                            best_score = reid_sim
                            best_tid = tid
                if best_tid is not None:
                    unmatched_tracks.remove(best_tid)
                    tr = self.tracks[best_tid]
                    tr.update(
                        bbox,
                        str(det["label"]),
                        float(det["confidence"]),  # type: ignore[arg-type]
                        emb,
                        frame_index,
                    )
                    output.append(self._format_detection(det, tr))
                else:
                    leftover.append((det, bbox, emb))
            return leftover

        unmatched_high = associate(high, allow_reid=True)
        _ = associate(low, allow_reid=False)

        # Spawn new tracks from unmatched high-confidence detections
        for det, bbox, emb in unmatched_high:
            tid = self._next_id
            self._next_id += 1
            cx = 0.5 * (bbox[0] + bbox[2])
            cy = 0.5 * (bbox[1] + bbox[3])
            tr = TrackState(
                track_id=tid,
                bbox=bbox,
                class_scores={str(det["label"]): float(det["confidence"])},  # type: ignore[arg-type]
                confidence=float(det["confidence"]),  # type: ignore[arg-type]
                embedding=emb,
                history=[{"frame": frame_index, "cx": round(cx, 1), "cy": round(cy, 1)}],
            )
            self.tracks[tid] = tr
            output.append(self._format_detection(det, tr))

        # Prune expired tracks
        for tid in list(self.tracks.keys()):
            if self.tracks[tid].lost_frames > self.max_lost_frames:
                del self.tracks[tid]

        return output

    @staticmethod
    def _format_detection(det: dict[str, object], tr: TrackState) -> dict[str, object]:
        enriched = dict(det)
        enriched["trackId"] = tr.track_id
        enriched["label"] = tr.dominant_label
        enriched["confidence"] = round(tr.confidence, 4)
        enriched["bbox"] = {
            "x1": round(tr.bbox[0], 1),
            "y1": round(tr.bbox[1], 1),
            "x2": round(tr.bbox[2], 1),
            "y2": round(tr.bbox[3], 1),
        }
        enriched["trajectory"] = list(tr.history[-30:])
        return enriched
