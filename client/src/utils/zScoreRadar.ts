// Display scale with -3 anchored at the center and +2 near the outer ring
export const Z_SCORE_CONFIG = {
  MIN_VALUE: -3,
  MAX_VALUE: 2,
  VISUAL_BOOST: 1,
  RADAR_RADIUS: 120
} as const;

export function valueToFraction(value: number): number {
  if (!Number.isFinite(value)) return 0.5;
  const boosted = value * Z_SCORE_CONFIG.VISUAL_BOOST;
  // Map -3 -> 0 (center), +2 -> 1 (outer), with linear spacing
  const span = Z_SCORE_CONFIG.MAX_VALUE - Z_SCORE_CONFIG.MIN_VALUE;
  const normalized = (boosted - Z_SCORE_CONFIG.MIN_VALUE) / span;
  return Math.min(Math.max(normalized, 0), 1);
}

export function formatZScore(value: number, precision: number = 2): string {
  if (!Number.isFinite(value)) return "-";
  const fixed = value.toFixed(precision);
  const trimmed = fixed.replace(/\.?0+$/, "");
  return `${value >= 0 ? "+" : ""}${trimmed}`;
}

export const RING_VALUES = [-3, -2, -1, 0, 1, 2];
export const RING_FRACTIONS = RING_VALUES.map(valueToFraction);
export const RING_LABELS = RING_VALUES.map((v) => {
  const label = v.toFixed(0);
  if (v === 0) return "0";
  return v > 0 ? `+${label}` : label;
});
