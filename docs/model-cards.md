# Model Cards — Visionlytics Production Models

## 1. `RT-DETRv2-R18vd-INT8` (Balanced & Max Accuracy Default)
- **Source Checkpoint**: `PekingU/rtdetr_v2_r18vd` / `onnx-community/rtdetr_v2_r18vd-ONNX`
- **Licence**: **Apache-2.0** (Permissive; commercial self-hosting allowed without open-source copyleft obligations)
- **Architecture**: Real-Time Detection Transformer v2 with ResNet-18-vd backbone and dynamic query selection, quantized to INT8 (`20.02 MB`).
- **Training Data**: COCO 2017 (`train2017`, 80 object categories).
- **Calibration**: Temperature scaling ($T = 1.15$). Detections below the user-configurable calibrated confidence threshold (default `0.50`) are explicitly marked `uncertain: true` with a dashed reticle in the UI rather than silently presented as high-certainty predictions.
- **Measured Evaluation Metrics** (Apple M4 ARM64 CPU via `uv run python -m visionlytics_ml.eval_harness`):
  - `mAP50`: **0.9143** (`91.4%`)
  - `mAP50-95`: **0.8514** (`85.1%`)
  - `Person Count MAE`: **0.00** (`100%` exact match on golden street & close-subject test scenes)
  - `Latency`: **p50 = 169.06 ms**, **p95 = 175.17 ms** (end-to-end including foreground mask + CIELAB k-means + CIEDE2000 colour matching)
- **Known Limitations**:
  - Small objects occupying $< 1.5\%$ of frame height require enabling **Small-object tiled mode (SAHI 2×2)**, which multiplies inference latency by $\sim 4\times$.

---

## 2. `YOLOS-Tiny-INT8` (Fast / Live Stream Preset)
- **Source Checkpoint**: `hustvl/yolos-tiny` / `Xenova/yolos-tiny`
- **Licence**: **Apache-2.0**
- **Architecture**: Vision Transformer (`DeiT-Tiny` backbone) trained for bipartite object detection (`6.46 MB` INT8).
- **Measured Latency** (Apple M4 ARM64 CPU):
  - Pure detector pass (`320×320`): **p50 = 23.9 ms** (`41.8 FPS`), **p95 = 25.5 ms**
  - End-to-end with CIELAB colour extraction (`416×416`): **p50 = 98.14 ms** (`10.19 FPS`), **p95 = 100.74 ms**
- **Known Limitations**:
  - Lower localization recall on heavily occluded crowds compared to `RT-DETRv2-R18vd`.

---

## 3. Foreground Colour & Attire Pipeline (`CIELAB` + `CIEDE2000`)
- **Algorithm**:
  1. Border-ring background modeling + elliptical spatial mask (or explicit segmentation mask) to exclude bounding-box background padding.
  2. Gray-world illuminant white-balance normalization (channel gains bounded to $[0.88, 1.12]$).
  3. Rejection of specular glare ($L^* > 96, C^* < 6$) and deep shadow noise ($L^* < 6$).
  4. Deterministic $k$-means ($k \le 3$) in CIE 1976 $L^*a^*b^*$ (D65) space.
  5. Perceptual matching against a 28-colour human palette via the full **CIEDE2000 ($\Delta E_{00}$)** formula.
- **Measured Accuracy**: **85.71%** (`0.8571`) exact human colour name match across 56 warm/cool illuminant-shifted and background-cluttered test patches.
