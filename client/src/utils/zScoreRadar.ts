export const Z_SCORE_CONFIG = {
  MIN_VALUE: -1,
  MAX_VALUE: 1,
  VALUE_SPAN: 2,
  VISUAL_BOOST: 1,
  RADAR_RADIUS: 120
} as const;

export function valueToFraction(value: number): number {
  if (!Number.isFinite(value)) return 0.5;
  const boosted = value * Z_SCORE_CONFIG.VISUAL_BOOST;
  const normalized = (boosted - Z_SCORE_CONFIG.MIN_VALUE) / Z_SCORE_CONFIG.VALUE_SPAN;
  return Math.min(Math.max(normalized, 0), 1);
}

export function formatZScore(value: number, precision: number = 2): string {
  if (!Number.isFinite(value)) return "-";
  const fixed = value.toFixed(precision);
  const trimmed = fixed.replace(/\.?0+$/, "");
  return `${value >= 0 ? "+" : ""}${trimmed}`;
}

export const RING_VALUES = [-1, -0.5, 0, 0.5, 1];
export const RING_FRACTIONS = RING_VALUES.map(valueToFraction);
export const RING_LABELS = RING_VALUES.map((v) => {
  const label = Math.abs(v) === 1 ? v.toFixed(0) : v.toFixed(1).replace(/\.0$/, "");
  if (v === 0) return "0";
  return v > 0 ? `+${label}` : label;
});
