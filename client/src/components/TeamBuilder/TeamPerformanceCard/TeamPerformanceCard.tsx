import { useEffect, useRef, useState } from "react";
import type { TeamWeaknessResponse } from "@/api/players";
import { Card } from "@/components";
import { Modal } from "@/components/Modal";
import styles from "./TeamPerformanceCard.module.css";
import typography from "@/styles/typography.module.css";

type AxisLabelPosition = {
  offsetMultiplier?: number;
  xOffset?: number;
  yOffset?: number;
  anchor?: "start" | "middle" | "end";
};

type AxisLabelConfig = {
  key: keyof TeamWeaknessResponse;
  label: string;
  position?: AxisLabelPosition;
};

const STAT_LABELS: AxisLabelConfig[] = [
  { key: "strikeout_rate", label: "Strikeout Rate" },
  {
    key: "walk_rate",
    label: "Walk Rate",
    position: { xOffset: -20, yOffset: 4, anchor: "start" }
  },
  { key: "isolated_power", label: "Iso Power" },
  { key: "on_base_percentage", label: "On Base %" },
  {
    key: "base_running",
    label: "Base Running",
    position: { xOffset: 6, yOffset: 6, anchor: "end", offsetMultiplier: 1.22 }
  }
];

const MIN_VALUE = -3;
const MAX_VALUE = 2;
const VALUE_SPAN = MAX_VALUE - MIN_VALUE;
const BASELINE_VALUE = 0;

/**
 * Maps a numeric value to a normalized fraction between 0 and 1 based on the configured min/max range.
 *
 * @param value - The value to normalize; non-finite values are treated specially.
 * @returns A number in [0, 1] representing `value`'s relative position where 0 corresponds to `MIN_VALUE` and 1 corresponds to `MAX_VALUE`. Non-finite inputs return `0.5`. */
function valueToFraction(value: number) {
  if (!Number.isFinite(value)) return 0.5;
  const fraction = (value - MIN_VALUE) / VALUE_SPAN;
  return Math.min(Math.max(fraction, 0), 1);
}

const RING_VALUES = [MIN_VALUE, -2, -1, 0, 1, MAX_VALUE];
const RING_FRACTIONS = RING_VALUES.map(v => valueToFraction(v));
const BASELINE_FRACTION = valueToFraction(BASELINE_VALUE);
const RING_LABEL_VALUES = Array.from(new Set([...RING_VALUES, BASELINE_VALUE])).sort((a, b) => a - b);
const RADAR_SIZE = 320;
const RADAR_CENTER = { x: RADAR_SIZE / 2, y: RADAR_SIZE / 2 };
const RADAR_RADIUS = 120;
const AXIS_LABEL_OFFSET = 1.32;

type TeamPerformanceCardProps = {
  weakness: TeamWeaknessResponse | null;
  loading: boolean;
  hasLineup: boolean;
};

/**
 * Render a "Team Performance" card that visualizes a lineup's per-stat deviations from league averages using a radar chart and stat summaries.
 *
 * The component displays loading and empty-lineup states, animates polygon morphing when weakness data changes, highlights the worst axes, and includes league-average and lineup polygons with ring and axis labels.
 *
 * @param weakness - Optional team weakness metrics keyed by stat; used to compute radar fractions and stat summaries.
 * @param loading - When true, shows an analyzing state and preserves the previous weakness for smooth transitions.
 * @param hasLineup - When false, shows a prompt to add players instead of the performance visualization.
 * @returns The rendered Team Performance card element.
 */
export function TeamPerformanceCard({
  weakness,
  loading,
  hasLineup
}: TeamPerformanceCardProps) {
  const previousWeaknessRef = useRef<TeamWeaknessResponse | null>(null);
  const [animatedFractions, setAnimatedFractions] = useState<number[]>([]);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Store previous weakness for interpolation
  useEffect(() => {
    if (weakness && !loading) {
      previousWeaknessRef.current = weakness;
    }
  }, [weakness, loading]);

  // Use previous weakness if currently loading to prevent flicker
  const displayWeakness = loading && previousWeaknessRef.current 
    ? previousWeaknessRef.current 
    : weakness;

  // Animate polygon morphing
  useEffect(() => {
    if (!displayWeakness) return;

    const targetFractions = getValueFractions(displayWeakness);
    
    // Initialize if first render
    if (animatedFractions.length === 0) {
      setAnimatedFractions(targetFractions);
      return;
    }

    // Animate from current to target
    const startFractions = [...animatedFractions];
    const startTime = performance.now();
    const duration = 800; // 800ms animation

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-in-out)
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      const interpolated = startFractions.map((start, i) => {
        const target = targetFractions[i];
        return start + (target - start) * eased;
      });

      setAnimatedFractions(interpolated);

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [displayWeakness]);

  if (!hasLineup) {
    return (
      <Card title="Team Performance" subtitle="Your lineup compared to league averages">
        <div className={styles.stateMessage}>Add players to your lineup to view performance.</div>
      </Card>
    );
  }

  if (loading && !previousWeaknessRef.current) {
    return (
      <Card title="Team Performance" subtitle="Your lineup compared to league averages">
        <div className={styles.stateMessage}>Analyzing lineup…</div>
      </Card>
    );
  }

  if (!displayWeakness) {
    return (
      <Card title="Team Performance" subtitle="Your lineup compared to league averages">
        <div className={styles.stateMessage}>Unable to compute performance.</div>
      </Card>
    );
  }

  const percentileFractions = getValueFractions(displayWeakness);
  
  // Use animated fractions for rendering, fall back to static if not initialized
  const displayFractions = animatedFractions.length > 0 ? animatedFractions : percentileFractions;
  
  const rankedAxes = percentileFractions
    .map((value, idx) => ({ value, idx }))
    .sort((a, b) => a.value - b.value);
  const worstAxisIndex = rankedAxes[0]?.idx ?? null;
  const secondWorstAxisIndex = rankedAxes[1]?.idx ?? null;
  const leagueBaselinePolygon = Array(STAT_LABELS.length).fill(BASELINE_FRACTION);

  const getStatColorClass = (value: number) => {
    if (value >= 1.5) return styles.statSuperGood;
    if (value >= 0.5) return styles.statGood;
    if (value >= -0.5) return styles.statNeutral;
    if (value >= -1.5) return styles.statBad;
    return styles.statSuperBad;
  };

  // Convert standard deviation to approximate percentile
  // Using normal distribution: mean=0, std=1
  const getPercentile = (value: number): number => {
    // Approximate percentile using error function approximation
    // For standard normal distribution
    const t = 1 / (1 + 0.2316419 * Math.abs(value));
    const d = 0.3989423 * Math.exp(-value * value / 2);
    const probability = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    
    let percentile;
    if (value >= 0) {
      percentile = (1 - probability) * 100;
    } else {
      percentile = probability * 100;
    }
    
    return Math.round(percentile);
  };

  // Render performance content - reusable for both card and modal
  const renderPerformanceContent = (isModal = false) => {
    return (
      <div className={`${styles.performanceLayout} ${isModal ? styles.performanceLayoutModal : ""}`}>
        <div className={`${styles.statsColumn} ${isModal ? styles.statsColumnModal : ""}`}>
          {STAT_LABELS.map(({ key, label }) => {
            const rawValue = displayWeakness[key];
            const percentile = getPercentile(rawValue);
            return (
              <div key={key} className={`${styles.statBlock} ${isModal ? styles.statBlockModal : ""}`}>
                <div className={`${styles.statLabel} ${isModal ? styles.statLabelModal : ""}`}>{label}</div>
                <div className={`${styles.statValueContainer} ${isModal ? styles.statValueContainerModal : ""}`}>
                  <div className={`${styles.statValueGroup} ${isModal ? styles.statValueGroupModal : ""}`}>
                    <div className={`${styles.statValue} ${getStatColorClass(rawValue)} ${isModal ? styles.statValueModal : ""}`}>
                      {formatValueLabel(rawValue)}
                    </div>
                    <div className={`${styles.statSubLabel} ${isModal ? styles.statSubLabelModal : ""}`}>std dev</div>
                  </div>
                  <div className={`${styles.statPercentile} ${isModal ? styles.statPercentileModal : ""}`}>
                    <div className={`${styles.percentileValue} ${isModal ? styles.percentileValueModal : ""}`}>
                      <span className={getStatColorClass(rawValue)}>{percentile}</span>
                      <span className={`${styles.percentileSuffix} ${isModal ? styles.percentileSuffixModal : ""}`}>th</span>
                    </div>
                    <span className={`${styles.percentileLabel} ${isModal ? styles.percentileLabelModal : ""}`}>percentile</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className={`${styles.radarSection} ${isModal ? styles.radarSectionModal : ""}`}>
          <div className={`${styles.radarChartWrapper} ${isModal ? styles.radarChartWrapperModal : ""}`}>
            <svg
              viewBox={`0 0 ${RADAR_SIZE} ${RADAR_SIZE}`}
              style={{ maxWidth: isModal ? "600px" : "320px", width: "100%", height: "auto", overflow: "visible" }}
            >
            {/* rings */}
            {RING_FRACTIONS.map((fraction, i) => (
              <polygon
                key={`ring-${i}`}
                points={buildRingPolygon(fraction)}
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1"
              />
            ))}
            {/* axis lines */}
            {STAT_LABELS.map((_, idx) => {
              const { x, y } = getPointForFraction(1, idx);
              return (
                <line
                  key={`axis-${idx}`}
                  x1={RADAR_CENTER.x}
                  y1={RADAR_CENTER.y}
                  x2={x}
                  y2={y}
                  stroke="rgba(255,255,255,0.12)"
                  strokeWidth="1"
                />
              );
            })}
            {/* league average polygon */}
            {renderRadarPolygon(leagueBaselinePolygon, {
              fill: "rgba(255, 173, 74, 0.18)",
              stroke: "rgba(255, 198, 124, 0.9)",
              strokeWidth: 1.5,
              className: styles.leaguePolygon
            }, "league-polygon")}
            {/* team polygon */}
            {renderRadarPolygon(displayFractions, {
              fill: "rgba(109,123,255,0.3)",
              stroke: "#6d7bff",
              strokeWidth: 2,
              className: styles.teamPolygon
            }, "team-polygon")}
            {/* baseline (midpoint) ring */}
            <polygon
              points={buildRingPolygon(BASELINE_FRACTION)}
              fill="none"
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="1"
              strokeDasharray="6 4"
            />
            {/* ring labels */}
            {RING_LABEL_VALUES.map((value) => {
              const fraction = valueToFraction(value);
              const isBaseline = Math.abs(value - BASELINE_VALUE) < 1e-6;
              const offset = isBaseline ? 6 : value === MAX_VALUE ? -10 : value === MIN_VALUE ? 14 : -4;
              const y = RADAR_CENTER.y - RADAR_RADIUS * fraction + offset;
              return (
                <text
                  key={`ring-label-${value}`}
                  x={RADAR_CENTER.x}
                  y={y}
                  textAnchor="middle"
                  className={`${styles.ringLabel} ${isBaseline ? styles.ringLabelAverage : ""} ${isModal ? styles.ringLabelModal : ""}`}
                >
                  {formatValueTick(value)}{isBaseline ? " (avg)" : ""}
                </text>
              );
            })}
            {/* axis labels */}
            {STAT_LABELS.map((axis, idx) => {
              const { position } = axis;
              const offsetMultiplier = position?.offsetMultiplier ?? AXIS_LABEL_OFFSET;
              let { x, y } = getPointForFraction(offsetMultiplier, idx, false);
              x += position?.xOffset ?? 0;
              y += position?.yOffset ?? 0;
              let anchor: "start" | "end" | "middle";
              const cosine = Math.cos(getAngle(idx));
              if (position?.anchor) anchor = position.anchor; else if (Math.abs(cosine) < 0.15) anchor = "middle"; else anchor = cosine > 0 ? "start" : "end";
              const rawValue = displayWeakness[axis.key];
              let labelClass = styles.axisLabel;
              if (idx === worstAxisIndex) labelClass = styles.axisLabelSevere; else if (idx === secondWorstAxisIndex) labelClass = styles.axisLabelWarn;
              if (isModal) labelClass = `${labelClass} ${styles.axisLabelModal}`;
              const scoreText = formatValueLabel(rawValue);
              const deficitDescription = describeWeakness(rawValue);
              const strikeoutNote = axis.key === "strikeout_rate" ? "Lower strikeout rate plots farther out." : null;
              return (
                <text
                  key={`axis-label-${axis.key}`}
                  x={x}
                  y={y}
                  textAnchor={anchor}
                  className={labelClass}
                >
                  {axis.label}
                  <title>{[`${axis.label}: ${scoreText}`, deficitDescription, strikeoutNote].filter(Boolean).join(" • ")}</title>
                </text>
              );
            })}
            </svg>
          </div>
          <div className={`${styles.radarLegend} ${isModal ? styles.radarLegendModal : ""}`}>
            <span className={styles.legendItem}>
              <span className={styles.legendDot} style={{ backgroundColor: 'rgba(255, 198, 124, 0.9)' }}></span>
              League Average
            </span>
            <span className={styles.legendItem}>
              <span className={styles.legendDot} style={{ backgroundColor: '#6d7bff' }}></span>
              Your Lineup
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      <Card 
        title="Team Performance" 
        subtitle="Your lineup compared to league averages"
        headerAction={
          <button 
            className={styles.expandBtn}
            onClick={() => setIsModalOpen(true)}
          >
            Expand Metrics
          </button>
        }
      >
        {renderPerformanceContent(false)}
      </Card>
      
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} className={styles.modalContentWrapper}>
        <div className={styles.modalHeader}>
          <div className={styles.modalHeaderContent}>
            <div className={`${typography.heading3} ${styles.modalTitle}`}>Team Performance</div>
            <div className={`${typography.bodySmall} ${typography.muted} ${styles.modalSubtitle}`}>Your lineup compared to league averages</div>
          </div>
        </div>
        {renderPerformanceContent(true)}
      </Modal>
    </>
  );
}

type PolygonStyle = {
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  className?: string;
  strokeDasharray?: string;
};

/**
 * Renders an SVG polygon for a radar chart from per-axis fractions.
 *
 * @param fractions - Array of fractions (0–1) for each axis, ordered to match the chart axes.
 * @param style - Optional polygon styling (fill, stroke, strokeWidth, className, strokeDasharray).
 * @param key - Optional React key applied to the polygon element.
 * @returns The SVG <polygon> element representing the radar polygon.
 */
function renderRadarPolygon(fractions: number[], style?: PolygonStyle, key?: string) {
  const points = buildPolygonPoints(fractions);

  return (
    <polygon
      key={key}
      points={points}
      fill={style?.fill ?? "none"}
      stroke={style?.stroke ?? "#6d7bff"}
      strokeWidth={style?.strokeWidth ?? 2}
      strokeDasharray={style?.strokeDasharray}
      className={style?.className}
      style={{
        transformOrigin: 'center',
        willChange: 'auto'
      }}
    />
  );
}

/**
 * Compute the angle in radians for a given radar axis index, with index 0 positioned at the top.
 *
 * @param axisIndex - Zero-based index of the axis around the radar
 * @returns The angle in radians for that axis; angles increase clockwise as the index increases
 */
function getAngle(axisIndex: number) {
  return (2 * Math.PI * axisIndex) / STAT_LABELS.length - Math.PI / 2;
}

/**
 * Computes the SVG coordinate on the radar for a given radial fraction and axis.
 *
 * @param fraction - Fraction of the radar radius (0 = center, 1 = outer edge); values outside [0,1] are honored only when `clamp` is false.
 * @param axisIndex - Zero-based index of the axis around the radar (0 corresponds to the top axis).
 * @param clamp - When true, restricts `fraction` to the [0,1] range before conversion.
 * @returns An object with `x` and `y` coordinates in the radar's SVG coordinate space.
 */
function getPointForFraction(fraction: number, axisIndex: number, clamp: boolean = true) {
  const value = clamp ? Math.min(Math.max(fraction, 0), 1) : fraction;
  const angle = getAngle(axisIndex);
  const r = Math.max(value, 0) * RADAR_RADIUS;
  return {
    x: RADAR_CENTER.x + r * Math.cos(angle),
    y: RADAR_CENTER.y + r * Math.sin(angle),
  };
}

/**
 * Builds an SVG-compatible points string from radial fractions for each axis.
 *
 * @param fractions - Array of radial fractions (typically 0–1) where each entry corresponds to an axis index and represents distance from the radar center.
 * @returns A space-separated string of `"x,y"` coordinate pairs suitable for an SVG `points` attribute (e.g. `"x1,y1 x2,y2 …"`).
 */
function buildPolygonPoints(fractions: number[]) {
  return fractions
    .map((fraction, idx) => {
      const { x, y } = getPointForFraction(fraction, idx);
      return `${x},${y}`;
    })
    .join(" ");
}

/**
 * Create the SVG polygon point string for a radar chart ring at a uniform radial fraction.
 *
 * @param fraction - Radial fraction (0 to 1) describing distance from center where the ring should be placed
 * @returns A space-separated list of `x,y` coordinate pairs suitable for an SVG polygon `points` attribute
 */
function buildRingPolygon(fraction: number) {
  return buildPolygonPoints(Array(STAT_LABELS.length).fill(fraction));
}

/**
 * Normalizes a raw weakness score into a display-ready numeric value.
 *
 * @param value - The raw weakness score which may be non-finite or highly precise
 * @returns `BASELINE_VALUE` when `value` is not finite; otherwise `value` rounded to three significant digits
 */
function weaknessToValue(value: number) {
  if (!Number.isFinite(value)) return BASELINE_VALUE;
  return Number(value.toPrecision(3));
}

/**
 * Convert a team's weakness scores into normalized 0–1 fractions for each radar axis.
 *
 * @param weakness - Object mapping stat keys to numeric weakness scores used to compute axis fractions
 * @returns An array of numbers between 0 and 1 representing the fraction for each axis, in the same order as `STAT_LABELS`
 */
function getValueFractions(weakness: TeamWeaknessResponse) {
  return STAT_LABELS.map(({ key }) => valueToFraction(weaknessToValue(weakness[key])));
}

/**
 * Describe how a numeric statistic compares to the league average.
 *
 * @param value - Signed numeric difference from league average (positive means worse than league average); non-finite values indicate unavailable data
 * @returns A human-readable message: `"Difference vs league unavailable"` for non-finite input, `"On par with league average"` for differences under 0.5 points, or `"<n> pts below league average"` / `"<n> pts above league average"` where `n` is rounded to an integer for values >= 10 points or shown with one decimal otherwise
 */
function describeWeakness(value: number) {
  if (!Number.isFinite(value)) {
    return "Difference vs league unavailable";
  }

  const points = Math.abs(value * 100);
  if (points < 0.5) {
    return "On par with league average";
  }

  const direction = value >= 0 ? "below league average" : "above league average";
  const rounded =
    points >= 10 ? Math.round(points).toString() : points.toFixed(1).replace(/\.0$/, "");
  return `${rounded} pts ${direction}`;
}

/**
 * Format a numeric performance value into a display-ready label.
 *
 * @param value - Performance metric (e.g., a standard-deviation-like score) to format for display
 * @returns A string containing the formatted representation of `value` suitable for UI presentation
 */
function formatValueLabel(value: number) {
  return `${formatValueNumber(value)}`;
}

/**
 * Format a numeric axis tick label for display.
 *
 * @param value - The numeric value to format for an axis tick
 * @returns A string suitable for use as a tick label
 */
function formatValueTick(value: number) {
  return `${formatValueNumber(value)}`;
}

/**
 * Format a numeric value into a compact signed string for display.
 *
 * @param value - The number to format.
 * @returns `"-"` for non-finite inputs; otherwise a string with a leading `"+"` for values >= 0 (no sign for negative values), rounded to two decimal places with a trailing `.00` removed when present.
 */
function formatValueNumber(value: number) {
  if (!Number.isFinite(value)) return "-";
  return (value >= 0 ? "+" : "") + value.toFixed(2).replace(/\.00$/, "");
}