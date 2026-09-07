"""
Modern Vector SVG Icons for Visionlytics.

Provides clean, scalable, high-tech SVG icons to replace emojis
across the application for a professional, enterprise-grade aesthetic.
"""

# ── Brand Identity Logo ──────────────────────────────────────────────────────
BRAND_LOGO_SVG = """<svg class="brand-logo-svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="brandHexGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#636ee6"/>
      <stop offset="50%" stop-color="#808cf7"/>
      <stop offset="100%" stop-color="#00b894"/>
    </linearGradient>
    <radialGradient id="opticGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="rgba(99, 110, 230, 0.4)"/>
      <stop offset="100%" stop-color="rgba(0, 184, 148, 0)"/>
    </radialGradient>
  </defs>
  <!-- Outer Hexagon Visor -->
  <polygon points="24,3 43,14 43,34 24,45 5,34 5,14"
           stroke="url(#brandHexGrad)" stroke-width="2.5"
           fill="rgba(15, 23, 42, 0.75)" stroke-linejoin="round"/>
  <!-- Concentric Optic Halo -->
  <circle cx="24" cy="24" r="13" fill="url(#opticGlow)"/>
  <circle cx="24" cy="24" r="10.5" stroke="#636ee6" stroke-width="1.8" stroke-dasharray="4 3"/>
  <!-- Biometric Scanner Core -->
  <circle cx="24" cy="24" r="5.5" fill="#00b894" fill-opacity="0.85"/>
  <circle cx="24" cy="24" r="2" fill="#ffffff"/>
  <!-- Crosshair Reticles -->
  <line x1="24" y1="8" x2="24" y2="11" stroke="#808cf7" stroke-width="2" stroke-linecap="round"/>
  <line x1="24" y1="37" x2="24" y2="40" stroke="#808cf7" stroke-width="2" stroke-linecap="round"/>
  <line x1="10" y1="24" x2="13" y2="24" stroke="#808cf7" stroke-width="2" stroke-linecap="round"/>
  <line x1="35" y1="24" x2="38" y2="24" stroke="#808cf7" stroke-width="2" stroke-linecap="round"/>
</svg>"""

# ── Feature Card Icons ───────────────────────────────────────────────────────
ICON_IMAGE_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="#636ee6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="18" height="18" rx="4" stroke-opacity="0.9"/>
  <circle cx="9" cy="9" r="2" fill="#636ee6" fill-opacity="0.3"/>
  <path d="M21 15l-5-5L5 21"/>
  <path d="M14 14l2-2 5 5"/>
</svg>"""

ICON_VIDEO_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="#a29bfe" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="4" width="20" height="16" rx="3" stroke-opacity="0.9"/>
  <polygon points="10 8 16 12 10 16 10 8" fill="#a29bfe" fill-opacity="0.75" stroke="#a29bfe"/>
  <line x1="2" y1="8" x2="6" y2="8"/>
  <line x1="18" y1="8" x2="22" y2="8"/>
  <line x1="2" y1="16" x2="6" y2="16"/>
  <line x1="18" y1="16" x2="22" y2="16"/>
</svg>"""

ICON_LIVE_CAMERA = """<svg viewBox="0 0 24 24" fill="none" stroke="#00b894" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M23 7l-7 5 7 5V7z" fill="#00b894" fill-opacity="0.25"/>
  <rect x="1" y="5" width="15" height="14" rx="3"/>
  <circle cx="8" cy="12" r="3" stroke-dasharray="3 2"/>
  <circle cx="8" cy="12" r="1.2" fill="#00b894"/>
</svg>"""

# ── Architecture Card Icons ──────────────────────────────────────────────────
ICON_COMPUTER_VISION = """<svg viewBox="0 0 24 24" fill="none" stroke="#636ee6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
  <circle cx="12" cy="12" r="3" fill="#636ee6" fill-opacity="0.25"/>
  <line x1="12" y1="2" x2="12" y2="5" stroke-dasharray="1 1"/>
  <line x1="12" y1="19" x2="12" y2="22" stroke-dasharray="1 1"/>
</svg>"""

ICON_FEATURE_ENGINEERING = """<svg viewBox="0 0 24 24" fill="none" stroke="#a29bfe" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
  <polyline points="2 17 12 22 22 17"/>
  <polyline points="2 12 12 17 22 12"/>
</svg>"""

ICON_MACHINE_LEARNING = """<svg viewBox="0 0 24 24" fill="none" stroke="#00b894" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <!-- Input nodes -->
  <circle cx="4" cy="6" r="2" fill="#00b894" fill-opacity="0.4"/>
  <circle cx="4" cy="18" r="2" fill="#00b894" fill-opacity="0.4"/>
  <!-- Hidden nodes -->
  <circle cx="12" cy="4" r="2" fill="#00b894" fill-opacity="0.6"/>
  <circle cx="12" cy="12" r="2" fill="#00b894" fill-opacity="0.8"/>
  <circle cx="12" cy="20" r="2" fill="#00b894" fill-opacity="0.6"/>
  <!-- Output node -->
  <circle cx="20" cy="12" r="2.5" fill="#00b894"/>
  <!-- Synaptic Edges -->
  <line x1="6" y1="6" x2="10" y2="4" stroke-opacity="0.6"/>
  <line x1="6" y1="6" x2="10" y2="12" stroke-opacity="0.6"/>
  <line x1="6" y1="18" x2="10" y2="12" stroke-opacity="0.6"/>
  <line x1="6" y1="18" x2="10" y2="20" stroke-opacity="0.6"/>
  <line x1="14" y1="4" x2="18" y2="11" stroke-opacity="0.7"/>
  <line x1="14" y1="12" x2="18" y2="12" stroke-opacity="0.9"/>
  <line x1="14" y1="20" x2="18" y2="13" stroke-opacity="0.7"/>
</svg>"""

# ── General Purpose Icons ────────────────────────────────────────────────────
ICON_TARGET = """<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#636ee6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10"/>
  <circle cx="12" cy="12" r="6"/>
  <circle cx="12" cy="12" r="2" fill="#636ee6"/>
</svg>"""

ICON_OBJECTIVES = """<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#00b894" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
  <line x1="4" y1="22" x2="4" y2="15"/>
</svg>"""
