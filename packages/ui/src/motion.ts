/**
 * Motion tokens. Every animated component imports from here so timing and
 * physics are defined exactly once. Durations mirror --duration-* in tokens.css.
 */
export const duration = {
  instant: 0.12,
  quick: 0.2,
  base: 0.32,
  slow: 0.4,
} as const;

export const ease = {
  out: [0.16, 1, 0.3, 1],
  inOut: [0.65, 0, 0.35, 1],
  snap: [0.2, 0, 0, 1],
} as const;

export const spring = {
  /** Keys and toggles: firm, no visible overshoot. */
  key: { type: "spring", stiffness: 520, damping: 34, mass: 0.6 },
  /** Shared-layout indicators (tabs, segmented controls). */
  indicator: { type: "spring", stiffness: 420, damping: 38 },
  /** Magnetic hover pull. Soft so it never feels like the button is fleeing. */
  magnet: { stiffness: 260, damping: 22, mass: 0.4 },
} as const;

/** Error shake: 4 decaying oscillations inside the 320ms budget. */
export const shake = {
  x: [0, -5, 5, -3, 3, 0],
  transition: { duration: duration.base, ease: [...ease.inOut] as [number, number, number, number] },
};
