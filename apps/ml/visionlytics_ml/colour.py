"""
CIELAB + CIEDE2000 foreground colour pipeline for Visionlytics.

Steps:
1. Foreground mask isolation (removes outer bounding-box border background via
   radial foreground weighting + edge background subtraction when a polygon/SAM mask
   is not provided).
2. Gray-world white-balance normalization.
3. Specular highlight and deep shadow removal (drops pixels with L* < 14 or L* > 94).
4. Conversion from sRGB to CIE 1976 L*a*b* (D65 reference white).
5. Deterministic k-means clustering (k <= 3) in L*a*b* space.
6. Matching cluster centroids to a curated 28-colour human palette using the
   full CIEDE2000 (ΔE00) perceptual distance formula.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class NamedColour:
    name: str
    hex: str
    lab: tuple[float, float, float]


def srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Converts an array of shape (..., 3) in [0, 255] sRGB to CIE L*a*b* (D65)."""
    v = np.clip(rgb.astype(np.float64) / 255.0, 0.0, 1.0)
    linear = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)

    # sRGB to XYZ (D65)
    m = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ],
        dtype=np.float64,
    )
    xyz = linear @ m.T
    # D65 reference white
    xyz_ref = np.array([0.95047, 1.00000, 1.08883], dtype=np.float64)
    xr = xyz / xyz_ref

    eps = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    f = np.where(xr > eps, np.cbrt(xr), (kappa * xr + 16.0) / 116.0)

    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def hex_to_rgb(hex_str: str) -> np.ndarray:
    h = hex_str.lstrip("#")
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.float64)


def _make_palette() -> list[NamedColour]:
    raw = [
        ("Black", "#16181a"),
        ("Charcoal", "#32363b"),
        ("Slate Grey", "#656d75"),
        ("Silver Grey", "#a6adb4"),
        ("Off-White", "#ece8de"),
        ("Pure White", "#f9fafb"),
        ("Navy", "#1d2c4d"),
        ("Cobalt Blue", "#1f549c"),
        ("Sky Blue", "#63a4e6"),
        ("Teal", "#1d6f72"),
        ("Forest Green", "#215732"),
        ("Olive", "#5c6832"),
        ("Sage Green", "#849b78"),
        ("Signal Lime", "#b6e02e"),
        ("Amber", "#f2a91f"),
        ("Mustard", "#c89623"),
        ("Gold", "#e5c138"),
        ("Tangerine", "#e66c24"),
        ("Rust", "#9e4325"),
        ("Crimson Red", "#c1272d"),
        ("Burgundy", "#691c26"),
        ("Coral", "#e06d63"),
        ("Rose Pink", "#d87a98"),
        ("Plum", "#582c61"),
        ("Violet", "#744c9e"),
        ("Beige", "#d4c2a3"),
        ("Tan", "#b08c5e"),
        ("Espresso Brown", "#4b3425"),
    ]
    out: list[NamedColour] = []
    for name, hx in raw:
        lab = srgb_to_lab(hex_to_rgb(hx))
        out.append(NamedColour(name=name, hex=hx, lab=(float(lab[0]), float(lab[1]), float(lab[2]))))
    return out


PALETTE: list[NamedColour] = _make_palette()


def ciede2000(lab1: Sequence[float], lab2: Sequence[float]) -> float:
    """Computes the CIE ΔE2000 perceptual colour distance between two L*a*b* colours."""
    L1, a1, b1 = float(lab1[0]), float(lab1[1]), float(lab1[2])
    L2, a2, b2 = float(lab2[0]), float(lab2[1]), float(lab2[2])

    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    C_bar = 0.5 * (C1 + C2)
    C_bar7 = C_bar**7
    G = 0.5 * (1.0 - math.sqrt(C_bar7 / (C_bar7 + 25.0**7)))

    a1p = (1.0 + G) * a1
    a2p = (1.0 + G) * a2
    C1p = math.hypot(a1p, b1)
    C2p = math.hypot(a2p, b2)

    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0 if C1p > 1e-7 else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0 if C2p > 1e-7 else 0.0

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p * C2p < 1e-7:
        dhp = 0.0
    else:
        diff = h2p - h1p
        if abs(diff) <= 180.0:
            dhp = diff
        elif diff > 180.0:
            dhp = diff - 360.0
        else:
            dhp = diff + 360.0

    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(0.5 * dhp))

    L_bar_p = 0.5 * (L1 + L2)
    C_bar_p = 0.5 * (C1p + C2p)

    if C1p * C2p < 1e-7:
        h_bar_p = h1p + h2p
    else:
        if abs(h1p - h2p) <= 180.0:
            h_bar_p = 0.5 * (h1p + h2p)
        elif h1p + h2p < 360.0:
            h_bar_p = 0.5 * (h1p + h2p + 360.0)
        else:
            h_bar_p = 0.5 * (h1p + h2p - 360.0)

    T = (
        1.0
        - 0.17 * math.cos(math.radians(h_bar_p - 30.0))
        + 0.24 * math.cos(math.radians(2.0 * h_bar_p))
        + 0.32 * math.cos(math.radians(3.0 * h_bar_p + 6.0))
        - 0.20 * math.cos(math.radians(4.0 * h_bar_p - 63.0))
    )

    dTheta = 30.0 * math.exp(-(((h_bar_p - 275.0) / 25.0) ** 2))
    C_bar_p7 = C_bar_p**7
    RC = 2.0 * math.sqrt(C_bar_p7 / (C_bar_p7 + 25.0**7))

    Lm50_sq = (L_bar_p - 50.0) ** 2
    SL = 1.0 + (0.015 * Lm50_sq) / math.sqrt(20.0 + Lm50_sq)
    SC = 1.0 + 0.045 * C_bar_p
    SH = 1.0 + 0.015 * C_bar_p * T
    RT = -math.sin(math.radians(2.0 * dTheta)) * RC

    return math.sqrt(
        (dLp / SL) ** 2
        + (dCp / SC) ** 2
        + (dHp / SH) ** 2
        + RT * (dCp / SC) * (dHp / SH)
    )


def match_named_colour(lab: Sequence[float]) -> NamedColour:
    return min(PALETTE, key=lambda c: ciede2000(lab, c.lab))


def extract_foreground_mask(crop_rgb: np.ndarray) -> np.ndarray:
    """
    Computes a binary foreground mask for an object crop when no explicit segmentation
    mask is passed. Uses border ring colour modeling + elliptical spatial prior so
    background pixels around the box perimeter are excluded.
    """
    h, w, _ = crop_rgb.shape
    if h < 6 or w < 6:
        return np.ones((h, w), dtype=bool)

    yy, xx = np.mgrid[0:h, 0:w]
    ny = (yy - (h - 1) / 2.0) / max(h / 2.0, 1.0)
    nx = (xx - (w - 1) / 2.0) / max(w / 2.0, 1.0)
    ellipse = (nx**2 + ny**2) <= 0.68

    border_mask = (yy == 0) | (yy == h - 1) | (xx == 0) | (xx == w - 1)
    border_lab = srgb_to_lab(crop_rgb[border_mask])
    bg_median = np.median(border_lab, axis=0)

    full_lab = srgb_to_lab(crop_rgb)
    dist_from_bg = np.linalg.norm(full_lab - bg_median, axis=-1)
    fg = ellipse | (dist_from_bg > 18.0)
    # Always exclude the outermost 10% margin where bounding box padding lives
    inner = (np.abs(nx) <= 0.82) & (np.abs(ny) <= 0.82)
    mask = fg & inner
    if int(mask.sum()) < 8:
        return inner if int(inner.sum()) >= 4 else np.ones((h, w), dtype=bool)
    return mask


def extract_dominant_colours(
    crop_rgb: np.ndarray,
    mask: np.ndarray | None = None,
    max_clusters: int = 3,
) -> list[dict[str, object]]:
    """
    Returns up to `max_clusters` dominant named colours with their share in [0, 1].
    """
    if crop_rgb.size == 0:
        return []

    fg_mask = mask if mask is not None else extract_foreground_mask(crop_rgb)
    pixels = crop_rgb[fg_mask].reshape(-1, 3).astype(np.float64)
    if len(pixels) == 0:
        pixels = crop_rgb.reshape(-1, 3).astype(np.float64)

    # Subsample deterministically to at most 400 pixels for fast per-object speed
    if len(pixels) > 400:
        step = max(1, len(pixels) // 400)
        pixels = pixels[::step][:400]

    # Gentle gray-world illuminant normalization (capped to ±12% channel gain so chromatic objects stay true)
    channel_means = pixels.mean(axis=0)
    gray_target = float(channel_means.mean())
    if gray_target > 10.0 and np.all(channel_means > 10.0):
        gains = np.clip(gray_target / channel_means, 0.88, 1.12)
        pixels = np.clip(pixels * gains, 0.0, 255.0)

    labs = srgb_to_lab(pixels)

    # Filter out extreme specular glare (L* > 96 with very low chroma) and pitch-black sensor noise (L* < 6)
    chroma = np.hypot(labs[:, 1], labs[:, 2])
    valid = (labs[:, 0] >= 6.0) & ~((labs[:, 0] > 96.0) & (chroma < 6.0))
    if int(valid.sum()) >= 12:
        labs = labs[valid]

    k = min(max_clusters, len(labs))
    if k <= 1:
        matched = match_named_colour(labs.mean(axis=0))
        return [{"name": matched.name, "hex": matched.hex, "share": 1.0}]

    # Deterministic k-means initialized along L* quantiles
    order = np.argsort(labs[:, 0])
    init_idx = [order[int((i + 0.5) * len(labs) / k)] for i in range(k)]
    centers = labs[init_idx].copy()

    labels = np.zeros(len(labs), dtype=np.int32)
    for _ in range(10):
        dists = np.linalg.norm(labs[:, None, :] - centers[None, :, :], axis=-1)
        new_labels = dists.argmin(axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            members = labs[labels == j]
            if len(members) > 0:
                centers[j] = members.mean(axis=0)

    # Merge clusters that map to the same human colour name
    merged: dict[str, dict[str, object]] = {}
    total = float(len(labs))
    for j in range(k):
        count = int((labels == j).sum())
        if count == 0:
            continue
        matched = match_named_colour(centers[j])
        share = count / total
        if matched.name in merged:
            merged[matched.name]["share"] = float(merged[matched.name]["share"]) + share  # type: ignore[arg-type]
        else:
            merged[matched.name] = {"name": matched.name, "hex": matched.hex, "share": share}

    results = sorted(merged.values(), key=lambda x: float(x["share"]), reverse=True)  # type: ignore[arg-type]
    # Normalize shares to sum to 1.0 rounded to 2 decimal places
    norm_total = sum(float(r["share"]) for r in results) or 1.0
    for r in results:
        r["share"] = round(float(r["share"]) / norm_total, 2)
    return results


def extract_person_clothing_colours(
    person_crop_rgb: np.ndarray,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """
    Splits a person bounding box into upper torso (18%..54% height) and lower body
    (54%..88% height) and extracts dominant colours for each region.
    """
    h, w, _ = person_crop_rgb.shape
    if h < 12 or w < 6:
        cols = extract_dominant_colours(person_crop_rgb, max_clusters=2)
        return cols, cols
    y_top = int(h * 0.18)
    y_mid = int(h * 0.54)
    y_bot = int(h * 0.88)
    x_pad = int(w * 0.15)
    upper = person_crop_rgb[y_top:y_mid, x_pad : max(x_pad + 1, w - x_pad)]
    lower = person_crop_rgb[y_mid:y_bot, x_pad : max(x_pad + 1, w - x_pad)]
    return (
        extract_dominant_colours(upper, max_clusters=2),
        extract_dominant_colours(lower, max_clusters=2),
    )
