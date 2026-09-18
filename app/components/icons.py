"""
Modern Vector SVG Icons for Visionlytics.

Provides clean, scalable SVG icons using the new ocean-blue/coral/teal
color palette for a premium light-themed interface.
"""

# ── Brand Identity Logo ──────────────────────────────────────────────────────
BRAND_LOGO_SVG = """<svg class="brand-logo-svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4A7DFF"/>
      <stop offset="50%" stop-color="#6B9FFF"/>
      <stop offset="100%" stop-color="#A78BFA"/>
    </linearGradient>
    <radialGradient id="lensGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="rgba(74, 125, 255, 0.3)"/>
      <stop offset="100%" stop-color="rgba(167, 139, 250, 0)"/>
    </radialGradient>
  </defs>
  <!-- Outer Circle -->
  <circle cx="24" cy="24" r="21"
          stroke="url(#brandGrad)" stroke-width="2.5"
          fill="rgba(255, 255, 255, 0.1)"/>
  <!-- Optic Halo -->
  <circle cx="24" cy="24" r="13" fill="url(#lensGlow)"/>
  <circle cx="24" cy="24" r="10.5" stroke="#6B9FFF" stroke-width="1.5" stroke-dasharray="4 3"/>
  <!-- Lens Core -->
  <circle cx="24" cy="24" r="5.5" fill="#4A7DFF" fill-opacity="0.85"/>
  <circle cx="24" cy="24" r="2" fill="#ffffff"/>
  <!-- Crosshairs -->
  <line x1="24" y1="8" x2="24" y2="12" stroke="#A78BFA" stroke-width="2" stroke-linecap="round"/>
  <line x1="24" y1="36" x2="24" y2="40" stroke="#A78BFA" stroke-width="2" stroke-linecap="round"/>
  <line x1="8" y1="24" x2="12" y2="24" stroke="#A78BFA" stroke-width="2" stroke-linecap="round"/>
  <line x1="36" y1="24" x2="40" y2="24" stroke="#A78BFA" stroke-width="2" stroke-linecap="round"/>
</svg>"""

# ── Feature Card Icons ───────────────────────────────────────────────────────
ICON_IMAGE_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="#4A7DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="18" height="18" rx="4" stroke-opacity="0.9"/>
  <circle cx="9" cy="9" r="2" fill="#4A7DFF" fill-opacity="0.2"/>
  <path d="M21 15l-5-5L5 21"/>
  <path d="M14 14l2-2 5 5"/>
</svg>"""

ICON_VIDEO_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="4" width="20" height="16" rx="3" stroke-opacity="0.9"/>
  <polygon points="10 8 16 12 10 16 10 8" fill="#A78BFA" fill-opacity="0.6" stroke="#A78BFA"/>
  <line x1="2" y1="8" x2="6" y2="8"/>
  <line x1="18" y1="8" x2="22" y2="8"/>
  <line x1="2" y1="16" x2="6" y2="16"/>
  <line x1="18" y1="16" x2="22" y2="16"/>
</svg>"""

ICON_LIVE_CAMERA = """<svg viewBox="0 0 24 24" fill="none" stroke="#2ECDA7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M23 7l-7 5 7 5V7z" fill="#2ECDA7" fill-opacity="0.2"/>
  <rect x="1" y="5" width="15" height="14" rx="3"/>
  <circle cx="8" cy="12" r="3" stroke-dasharray="3 2"/>
  <circle cx="8" cy="12" r="1.2" fill="#2ECDA7"/>
</svg>"""

# ── Architecture Card Icons ──────────────────────────────────────────────────
ICON_COMPUTER_VISION = """<svg viewBox="0 0 24 24" fill="none" stroke="#4A7DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
  <circle cx="12" cy="12" r="3" fill="#4A7DFF" fill-opacity="0.2"/>
  <line x1="12" y1="2" x2="12" y2="5" stroke-dasharray="1 1"/>
  <line x1="12" y1="19" x2="12" y2="22" stroke-dasharray="1 1"/>
</svg>"""

ICON_FEATURE_ENGINEERING = """<svg viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
  <polyline points="2 17 12 22 22 17"/>
  <polyline points="2 12 12 17 22 12"/>
</svg>"""

ICON_MACHINE_LEARNING = """<svg viewBox="0 0 24 24" fill="none" stroke="#2ECDA7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <!-- Input nodes -->
  <circle cx="4" cy="6" r="2" fill="#2ECDA7" fill-opacity="0.3"/>
  <circle cx="4" cy="18" r="2" fill="#2ECDA7" fill-opacity="0.3"/>
  <!-- Hidden nodes -->
  <circle cx="12" cy="4" r="2" fill="#2ECDA7" fill-opacity="0.5"/>
  <circle cx="12" cy="12" r="2" fill="#2ECDA7" fill-opacity="0.7"/>
  <circle cx="12" cy="20" r="2" fill="#2ECDA7" fill-opacity="0.5"/>
  <!-- Output node -->
  <circle cx="20" cy="12" r="2.5" fill="#2ECDA7"/>
  <!-- Edges -->
  <line x1="6" y1="6" x2="10" y2="4" stroke-opacity="0.5"/>
  <line x1="6" y1="6" x2="10" y2="12" stroke-opacity="0.5"/>
  <line x1="6" y1="18" x2="10" y2="12" stroke-opacity="0.5"/>
  <line x1="6" y1="18" x2="10" y2="20" stroke-opacity="0.5"/>
  <line x1="14" y1="4" x2="18" y2="11" stroke-opacity="0.6"/>
  <line x1="14" y1="12" x2="18" y2="12" stroke-opacity="0.8"/>
  <line x1="14" y1="20" x2="18" y2="13" stroke-opacity="0.6"/>
</svg>"""

# ── General Purpose Icons ────────────────────────────────────────────────────
ICON_TARGET = """<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#4A7DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10"/>
  <circle cx="12" cy="12" r="6"/>
  <circle cx="12" cy="12" r="2" fill="#4A7DFF"/>
</svg>"""

ICON_OBJECTIVES = """<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#2ECDA7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
  <line x1="4" y1="22" x2="4" y2="15"/>
</svg>"""
