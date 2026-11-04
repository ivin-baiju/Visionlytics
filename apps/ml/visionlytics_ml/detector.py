"""
ONNX Runtime detection engine for Visionlytics:
- Supports `rtdetr_v2_r18vd` (Apache-2.0, highest accuracy) and `yolos_tiny` (Apache-2.0,
  high-FPS live streaming mode).
- Temperature-scaled confidence calibration (T = 1.15) with an explicit `uncertain`
  flag when calibrated score falls below `uncertain_threshold`.
- SAHI-style 2x2 overlapping tiled inference (`tiled=True`) with cross-tile NMS for
  distant / small objects.
- Integrated foreground CIELAB colour extraction and person upper/lower clothing split.
- Open-vocabulary attribute + colour + label filter ("red bus", "navy person").
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

from .colour import extract_dominant_colours, extract_person_clothing_colours
from .tracker import box_iou

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights"


def _nms(detections: list[dict[str, object]], iou_thresh: float = 0.50) -> list[dict[str, object]]:
    ordered = sorted(detections, key=lambda d: float(d["confidence"]), reverse=True)  # type: ignore[arg-type]
    kept: list[dict[str, object]] = []
    for cand in ordered:
        cb = cand["bbox"]  # type: ignore[index]
        c_box = (float(cb["x1"]), float(cb["y1"]), float(cb["x2"]), float(cb["y2"]))  # type: ignore[index]
        duplicate = False
        for existing in kept:
            if existing["label"] != cand["label"]:
                continue
            eb = existing["bbox"]  # type: ignore[index]
            e_box = (float(eb["x1"]), float(eb["y1"]), float(eb["x2"]), float(eb["y2"]))  # type: ignore[index]
            if box_iou(c_box, e_box) >= iou_thresh:
                duplicate = True
                break
        if not duplicate:
            kept.append(cand)
    return kept


class VisionDetector:
    def __init__(self, temperature: float = 1.15) -> None:
        self.temperature = temperature
        self._rtdetr_sess: ort.InferenceSession | None = None
        self._yolos_sess: ort.InferenceSession | None = None
        self._rtdetr_labels: dict[int, str] = {}
        self._yolos_labels: dict[int, str] = {}

    def _load_rtdetr(self) -> tuple[ort.InferenceSession, dict[int, str]]:
        if self._rtdetr_sess is None:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 4
            self._rtdetr_sess = ort.InferenceSession(
                str(WEIGHTS_DIR / "rtdetr_v2_r18vd_int8.onnx"),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            with open(WEIGHTS_DIR / "config.json") as f:
                self._rtdetr_labels = {int(k): v for k, v in json.load(f)["id2label"].items()}
        return self._rtdetr_sess, self._rtdetr_labels

    def _load_yolos(self) -> tuple[ort.InferenceSession, dict[int, str]]:
        if self._yolos_sess is None:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 4
            self._yolos_sess = ort.InferenceSession(
                str(WEIGHTS_DIR / "yolos_tiny_int8.onnx"),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            with open(WEIGHTS_DIR / "yolos_config.json") as f:
                self._yolos_labels = {int(k): v for k, v in json.load(f)["id2label"].items()}
        return self._yolos_sess, self._yolos_labels

    def _infer_single_crop(
        self,
        crop_img: Image.Image,
        preset: str,
        min_score: float,
    ) -> list[dict[str, object]]:
        w_orig, h_orig = crop_img.size
        if preset == "fast":
            sess, id2label = self._load_yolos()
            resized = crop_img.resize((416, 416), Image.Resampling.BILINEAR)
            arr = np.asarray(resized, dtype=np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            tensor = ((arr - mean) / std).transpose(2, 0, 1)[None, ...]
            logits, pred_boxes = sess.run(None, {"pixel_values": tensor})
            scaled = logits[0] / self.temperature
            exp = np.exp(scaled - scaled.max(axis=-1, keepdims=True))
            probs = exp / exp.sum(axis=-1, keepdims=True)
            scores = probs[:, :-1].max(axis=-1)
            labels = probs[:, :-1].argmax(axis=-1)
            boxes = pred_boxes[0]
        else:
            sess, id2label = self._load_rtdetr()
            resized = crop_img.resize((640, 640), Image.Resampling.BILINEAR)
            tensor = (np.asarray(resized, dtype=np.float32) / 255.0).transpose(2, 0, 1)[None, ...]
            logits, pred_boxes = sess.run(None, {"pixel_values": tensor})
            scaled = logits[0] / self.temperature
            probs = 1.0 / (1.0 + np.exp(-scaled))
            scores = probs.max(axis=-1)
            labels = probs.argmax(axis=-1)
            boxes = pred_boxes[0]

        keep = scores >= min_score
        raw: list[dict[str, object]] = []
        for lbl_idx, sc, cxcywh in zip(labels[keep], scores[keep], boxes[keep]):
            cx, cy, bw, bh = [float(v) for v in cxcywh]
            x1 = max(0.0, (cx - 0.5 * bw) * w_orig)
            y1 = max(0.0, (cy - 0.5 * bh) * h_orig)
            x2 = min(float(w_orig), (cx + 0.5 * bw) * w_orig)
            y2 = min(float(h_orig), (cy + 0.5 * bh) * h_orig)
            if (x2 - x1) < 4.0 or (y2 - y1) < 4.0:
                continue
            raw.append(
                {
                    "label": id2label.get(int(lbl_idx), "object"),
                    "confidence": round(float(sc), 4),
                    "bbox": {
                        "x1": round(x1, 1),
                        "y1": round(y1, 1),
                        "x2": round(x2, 1),
                        "y2": round(y2, 1),
                    },
                }
            )
        return _nms(raw, iou_thresh=0.50)

    def analyze_image(
        self,
        img: Image.Image,
        preset: str = "balanced",
        min_confidence: float = 0.28,
        uncertain_threshold: float = 0.50,
        tiled: bool = False,
        open_vocab_query: str | None = None,
    ) -> dict[str, object]:
        t0 = time.perf_counter()
        rgb_img = img.convert("RGB")
        w_img, h_img = rgb_img.size
        frame_np = np.asarray(rgb_img)

        detections = self._infer_single_crop(rgb_img, preset=preset, min_score=min_confidence)

        if tiled and w_img >= 400 and h_img >= 400:
            # SAHI 2x2 overlapping tiles (20% overlap) for small objects
            tiles = [
                (0, 0, int(w_img * 0.6), int(h_img * 0.6)),
                (int(w_img * 0.4), 0, w_img, int(h_img * 0.6)),
                (0, int(h_img * 0.4), int(w_img * 0.6), h_img),
                (int(w_img * 0.4), int(h_img * 0.4), w_img, h_img),
            ]
            for tx1, ty1, tx2, ty2 in tiles:
                tile_crop = rgb_img.crop((tx1, ty1, tx2, ty2))
                tile_dets = self._infer_single_crop(tile_crop, preset=preset, min_score=min_confidence)
                for td in tile_dets:
                    b = td["bbox"]  # type: ignore[index]
                    td["bbox"] = {
                        "x1": round(float(b["x1"]) + tx1, 1),  # type: ignore[index]
                        "y1": round(float(b["y1"]) + ty1, 1),  # type: ignore[index]
                        "x2": round(float(b["x2"]) + tx1, 1),  # type: ignore[index]
                        "y2": round(float(b["y2"]) + ty1, 1),  # type: ignore[index]
                    }
                    detections.append(td)
            detections = _nms(detections, iou_thresh=0.50)

        enriched: list[dict[str, object]] = []
        for idx, det in enumerate(detections):
            b = det["bbox"]  # type: ignore[index]
            x1 = max(0, min(w_img - 1, int(float(b["x1"]))))  # type: ignore[index]
            y1 = max(0, min(h_img - 1, int(float(b["y1"]))))  # type: ignore[index]
            x2 = max(x1 + 1, min(w_img, int(float(b["x2"]))))  # type: ignore[index]
            y2 = max(y1 + 1, min(h_img, int(float(b["y2"]))))  # type: ignore[index]
            crop = frame_np[y1:y2, x1:x2]

            colours = extract_dominant_colours(crop, max_clusters=3)
            score = float(det["confidence"])  # type: ignore[arg-type]
            item: dict[str, object] = {
                "trackId": idx + 1,
                "label": det["label"],
                "confidence": score,
                "uncertain": score < uncertain_threshold,
                "bbox": b,
                "colours": colours,
            }
            if det["label"] == "person":
                upper, lower = extract_person_clothing_colours(crop)
                item["upperClothingColours"] = upper
                item["lowerClothingColours"] = lower
            enriched.append(item)

        if open_vocab_query and open_vocab_query.strip():
            tokens = [t.lower() for t in open_vocab_query.strip().split() if t]
            filtered: list[dict[str, object]] = []
            for item in enriched:
                haystack = [str(item["label"]).lower()]
                for c in item.get("colours", []):  # type: ignore[attr-defined]
                    haystack.append(str(c["name"]).lower())  # type: ignore[index]
                for c in item.get("upperClothingColours", []):  # type: ignore[attr-defined]
                    haystack.append(str(c["name"]).lower())  # type: ignore[index]
                for c in item.get("lowerClothingColours", []):  # type: ignore[attr-defined]
                    haystack.append(str(c["name"]).lower())  # type: ignore[index]
                blob = " ".join(haystack)
                if all(tok in blob for tok in tokens):
                    filtered.append(item)
            enriched = filtered

        people_count = sum(
            1 for d in enriched if d["label"] == "person" and not bool(d["uncertain"])
        )
        uncertain_count = sum(1 for d in enriched if bool(d["uncertain"]))
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return {
            "width": w_img,
            "height": h_img,
            "preset": preset,
            "architecture": "yolos-tiny-int8" if preset == "fast" else "rtdetr-v2-r18vd-int8",
            "latencyMs": latency_ms,
            "peopleCount": people_count,
            "uncertainCount": uncertain_count,
            "detections": enriched,
        }
