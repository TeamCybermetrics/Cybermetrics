import { useEffect, useRef, useState, useMemo } from "react";
import type { TeamWeaknessResponse } from "@/api/players";
import { Card } from "@/components";
import { formatZScore } from "@/utils/zScoreRadar";
import styles from "@/pages/RecommendationsPage/components/RecommendationsView.module.css";

type StatAxis = {
  key: keyof TeamWeaknessResponse;
  label: string;
};

type Props = {
  statKeys: StatAxis[];
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  highlightOrder: number[];
  loading: boolean;
  error: string | null;
  formatValue: (value: number) => string;
};

const RADAR_SIZE = 300;
const RADAR_CENTER = { x: RADAR_SIZE / 2, y: RADAR_SIZE / 2 };
const RADAR_RADIUS = 115;
const DEFAULT_RING_COUNT = 5;
const AXIS_LABEL_OFFSET = 1.25;
const SVG_PADDING = 28;

const LABEL_OVERRIDES: Partial<Record<
  keyof TeamWeaknessResponse,
  { xOffset?: number; yOffset?: number; anchor?: "start" | "middle" | "end"; offsetMultiplier?: number }
>> = {
  strikeout_rate: { xOffset: -16, yOffset: -6 },
  walk_rate: { xOffset: 40, anchor: "start" },
  base_running: { xOffset: -2, anchor: "end" },
  on_base_percentage: { yOffset: 14 },
  isolated_power: { yOffset: 10 },
};

/**
 * Renders a "Before/After" weakness radar with a side-by-side stat comparison and animates polygon transitions when data changes.
 *
 * @param statKeys - Array of stat axis descriptors ({ key, label }) that define radar axes.
 * @param baselineWeakness - Baseline (before) z-score values keyed by stat, or `null` if not available.
 * @param currentWeakness - Current (after) z-score values keyed by stat; required to render the radar.
 * @param highlightOrder - Tuple of two axis indices to visually emphasize (first = severe, second = warn).
 * @param loading - When `true`, shows a loading placeholder instead of the chart.
 * @param error - Optional error message to display in place of the chart.
 * @param formatValue - Formatter function for numeric stat values (e.g., std dev display).
 * @returns The rendered RecommendationsRadarCard element.
 */
export function RecommendationsRadarCard({
  statKeys,
  baselineWeakness,
  currentWeakness,
  highlightOrder,
  loading,
  error,
  formatValue,
}: Props) {
  const hasData = !!currentWeakness;
  const previousCurrentWeaknessRef = useRef<TeamWeaknessResponse | null>(null);
  const previousBaselineWeaknessRef = useRef<TeamWeaknessResponse | null>(null);
  const [animatedCurrentFractions, setAnimatedCurrentFractions] = useState<number[]>([]);
  const [animatedBaselineFractions, setAnimatedBaselineFractions] = useState<number[]>([]);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Compute scale and fractions (needed for hooks)
  const scaleData = currentWeakness ? computeScale(statKeys, baselineWeakness, currentWeakness) : null;
  const scaleMin = scaleData?.scaleMin ?? 0;
  const scaleMax = scaleData?.scaleMax ?? 1;
  const scaleSpan = scaleMax - scaleMin || 1;

  const toFraction = (value: number | undefined | null) => {
    if (value == null || Number.isNaN(value)) return 0.5;
    return clamp((value - scaleMin) / scaleSpan, 0, 1);
  };

  const targetCurrentFractions = useMemo(() => 
    currentWeakness ? statKeys.map(({ key }) => toFraction(currentWeakness[key])) : [],
    [currentWeakness, scaleMin, scaleMax]
  );
  const targetBaselineFractions = useMemo(() => 
    baselineWeakness ? statKeys.map(({ key }) => toFraction(baselineWeakness[key])) : null,
    [baselineWeakness, scaleMin, scaleMax]
  );

  // Store previous weakness for interpolation
  useEffect(() => {
    if (currentWeakness && !loading) {
      previousCurrentWeaknessRef.current = currentWeakness;
    }
    if (baselineWeakness && !loading) {
      previousBaselineWeaknessRef.current = baselineWeakness;
    }
  }, [currentWeakness, baselineWeakness, loading]);

  // Animate polygon morphing for current weakness
  useEffect(() => {
    if (!currentWeakness || targetCurrentFractions.length === 0) return;

    // Initialize if first render
    if (animatedCurrentFractions.length === 0) {
      setAnimatedCurrentFractions(targetCurrentFractions);
      return;
    }

    // Check if values actually changed
    const hasChanged = targetCurrentFractions.some((val, i) => 
      Math.abs(val - animatedCurrentFractions[i]) > 0.001
    );
    
    if (!hasChanged) return;

    const targetFractions = targetCurrentFractions;

    // Animate from current to target
    const startFractions = [...animatedCurrentFractions];
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

      setAnimatedCurrentFractions(interpolated);

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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentWeakness, targetCurrentFractions]);

  // Animate polygon morphing for baseline weakness
  useEffect(() => {
    if (!baselineWeakness || !targetBaselineFractions) {
      if (animatedBaselineFractions.length > 0) {
        setAnimatedBaselineFractions([]);
      }
      return;
    }

    // Initialize if first render
    if (animatedBaselineFractions.length === 0) {
      setAnimatedBaselineFractions(targetBaselineFractions);
      return;
    }

    // Check if values actually changed
    const hasChanged = targetBaselineFractions.some((val, i) => 
      Math.abs(val - animatedBaselineFractions[i]) > 0.001
    );
    
    if (!hasChanged) return;

    const targetFractions = targetBaselineFractions;

    // Animate from current to target
    const startFractions = [...animatedBaselineFractions];
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

      setAnimatedBaselineFractions(interpolated);

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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baselineWeakness, targetBaselineFractions]);

  // Use animated fractions for rendering, fall back to static if not initialized
  const currentFractions = animatedCurrentFractions.length > 0 ? animatedCurrentFractions : targetCurrentFractions;
  const baselineFractions = animatedBaselineFractions.length > 0 ? animatedBaselineFractions : targetBaselineFractions;

  // Early returns after all hooks
  if (loading) {
    return (
      <Card title="Before/After" subtitle="Weakness Radar">
        <div className={styles.radarPlaceholder}>Calculating…</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Before/After" subtitle="Weakness Radar">
        <div className={styles.radarPlaceholder}>{error}</div>
      </Card>
    );
  }

  if (!hasData) {
    return (
      <Card title="Before/After" subtitle="Weakness Radar">
        <div className={styles.radarPlaceholder}>Add players to view radar.</div>
      </Card>
    );
  }

  const ringValues = scaleData!.ringValues;
  const ringFractions = ringValues.map((value: number) => toFraction(value));
  const ringLabels = Array.from(new Set([...ringValues, 0]))
    .sort((a, b) => a - b);

  const getStatColorClass = (value: number) => {
    if (value >= 1.5) return styles.statSuperGood;
    if (value >= 0.5) return styles.statGood;
    if (value >= -0.5) return styles.statNeutral;
    if (value >= -1.5) return styles.statBad;
    return styles.statSuperBad;
  };

  const getPercentile = (value: number): number => {
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

  // Render radar content - reusable for both card and modal
  const renderRadarContent = (isModal = false) => {
    const modalSize = isModal ? 600 : RADAR_SIZE;
    const modalRadius = isModal ? 230 : RADAR_RADIUS;
    const modalCenter = { x: modalSize / 2, y: modalSize / 2 };
    const modalPadding = isModal ? SVG_PADDING * 2 : SVG_PADDING;
    const svgMaxWidth = isModal ? "600px" : "300px";

    return (
      <div className={`${styles.performanceLayout} ${isModal ? styles.performanceLayoutModal : ''}`}>
        <div className={styles.statsComparisonColumn}>
          {statKeys.map(({ key, label }) => {
            const baselineValue = baselineWeakness?.[key];
            const currentValue = currentWeakness![key];
            const baselinePercentile = baselineValue !== undefined ? getPercentile(baselineValue) : null;
            const currentPercentile = getPercentile(currentValue);
            
            // Calculate delta and its color
            const delta = baselineValue !== undefined ? currentValue - baselineValue : null;
            const getDeltaColorClass = () => {
              if (delta === null || Math.abs(delta) < 0.1) return styles.statNeutral;
              if (delta > 0.5) return styles.statSuperGood;
              if (delta > 0.2) return styles.statGood;
              if (delta < -0.5) return styles.statSuperBad;
              if (delta < -0.2) return styles.statBad;
              return styles.statNeutral;
            };
            
            return (
              <div key={key} className={styles.statComparisonBlock}>
                <div className={styles.statComparisonLabel}>{label}</div>
                <div className={styles.statComparisonRow}>
                  {/* Baseline (Before) */}
                  <div className={styles.statBeforeGroup}>
                    {baselineValue !== undefined ? (
                      <>
                        <div className={styles.statValueWithLabel}>
                          <div className={`${styles.statComparisonValue} ${getStatColorClass(baselineValue)}`}>
                            {formatValue(baselineValue)}
                          </div>
                          <div className={styles.statSubLabel}>std dev</div>
                        </div>
                        <div className={styles.statPercentileWithLabel}>
                          <div className={`${styles.statComparisonPercentile} ${getStatColorClass(baselineValue)}`}>
                            {baselinePercentile}<span className={styles.percentileSuffix}>th</span>
                          </div>
                          <div className={styles.statSubLabel}>percentile</div>
                        </div>
                      </>
                    ) : (
                      <div className={styles.statPlaceholder}>—</div>
                    )}
                  </div>
                  
                  {/* Delta and Arrow */}
                  <div className={styles.statDeltaArrow}>
                    {delta !== null && (
                      <div className={`${styles.statDelta} ${getDeltaColorClass()}`}>
                        {delta === 0 ? '0.00' : `${delta > 0 ? '+' : '-'}${Math.abs(delta).toFixed(2)}`}
                      </div>
                    )}
                    <div className={styles.statArrow}>→</div>
                  </div>
                  
                  {/* Current (After) */}
                  <div className={styles.statAfterGroup}>
                    <div className={styles.statValueWithLabel}>
                      <div className={`${styles.statComparisonValue} ${getStatColorClass(currentValue)}`}>
                        {formatValue(currentValue)}
                      </div>
                      <div className={styles.statSubLabel}>std dev</div>
                    </div>
                    <div className={styles.statPercentileWithLabel}>
                      <div className={`${styles.statComparisonPercentile} ${getStatColorClass(currentValue)}`}>
                        {currentPercentile}<span className={styles.percentileSuffix}>th</span>
                      </div>
                      <div className={styles.statSubLabel}>percentile</div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className={styles.radarChart}>
        <svg
          viewBox={`${-modalPadding} ${-modalPadding} ${modalSize + 2 * modalPadding} ${modalSize + 2 * modalPadding}`}
          style={{ width: "100%", maxWidth: svgMaxWidth, height: "auto", overflow: "visible" }}
        >
          {ringFractions.map((fraction, i) => (
            <polygon
              key={`ring-${i}`}
              points={buildRingPolygon(fraction, statKeys.length, modalRadius, modalCenter)}
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth={1}
            />
          ))}

          {statKeys.map((_, idx) => {
            const { x, y } = getPointForFraction(1, idx, statKeys.length, true, modalRadius, modalCenter);
            return (
              <line
                key={`axis-${idx}`}
                x1={modalCenter.x}
                y1={modalCenter.y}
                x2={x}
                y2={y}
                stroke="rgba(255,255,255,0.12)"
                strokeWidth={1}
              />
            );
          })}

          <polygon
            points={buildPolygonPoints(currentFractions, statKeys.length, modalRadius, modalCenter)}
            className={styles.teamPolygon}
          />

          {baselineFractions && (
            <polygon
              points={buildPolygonPoints(baselineFractions, statKeys.length, modalRadius, modalCenter)}
              className={styles.leaguePolygon}
            />
          )}

          <polygon
            points={buildRingPolygon(toFraction(0), statKeys.length, modalRadius, modalCenter)}
            fill="none"
            stroke="rgba(255,255,255,0.35)"
            strokeWidth={1}
            strokeDasharray="6 4"
          />

          {ringLabels.map((value) => {
            const fraction = toFraction(value);
            const isBaseline = Math.abs(value) < 1e-6;
            const y = modalCenter.y - modalRadius * fraction + (isBaseline ? 6 : -4);
            return (
              <text
                key={`ring-label-${value}`}
                x={modalCenter.x}
                y={y}
                textAnchor="middle"
                className={`${styles.ringLabel} ${isBaseline ? styles.ringLabelAverage : ""}`}
              >
                {formatZScore(value, 1)}
                {isBaseline ? " (avg)" : ""}
              </text>
            );
          })}

          {statKeys.map((axis, idx) => {
          const overrides = LABEL_OVERRIDES[axis.key];
          const offsetMultiplier = overrides?.offsetMultiplier ?? AXIS_LABEL_OFFSET;
          let { x, y } = getPointForFraction(offsetMultiplier, idx, statKeys.length, false, modalRadius, modalCenter);
          x += overrides?.xOffset ?? 0;
          y += overrides?.yOffset ?? 0;
          let anchor: "start" | "middle" | "end";
          const cosine = Math.cos(getAngle(idx, statKeys.length));
          if (overrides?.anchor) {
            anchor = overrides.anchor;
          } else if (Math.abs(cosine) < 0.15) {
            anchor = "middle";
          } else {
            anchor = cosine > 0 ? "start" : "end";
          }
            const value = currentWeakness![axis.key];
            let labelClass = styles.axisLabel;
            if (idx === highlightOrder[0]) labelClass = styles.axisLabelSevere;
            else if (idx === highlightOrder[1]) labelClass = styles.axisLabelWarn;

            return (
              <text
                key={`axis-label-${axis.key}`}
                x={x}
                y={y}
                textAnchor={anchor}
                className={labelClass}
              >
                {axis.label}
                <title>{`${axis.label}: ${formatZScore(value)}`}</title>
              </text>
            );
          })}
        </svg>
        <div className={styles.radarLegend}>
          <div className={styles.legendItem}>
            <div className={styles.legendDot} style={{ background: 'rgba(255, 198, 124, 0.9)' }}></div>
            <span>Baseline</span>
          </div>
          <div className={styles.legendItem}>
            <div className={styles.legendDot} style={{ background: '#6d7bff' }}></div>
            <span>Current</span>
          </div>
        </div>
      </div>
    </div>
    );
  };

  return (
    <>
    <Card 
      title="Roster Performance" 
      subtitle="Before/After Changes"
      headerAction={
        <button 
          className={styles.baselineBtn}
          onClick={() => setIsModalOpen(true)}
        >
          Expand Metrics
        </button>
      }
    >
      {renderRadarContent(false)}
    </Card>
    {isModalOpen && (
      <div 
        className={styles.modalOverlay}
        onClick={() => setIsModalOpen(false)}
      >
        <div 
          className={styles.modalContent}
          onClick={(e) => e.stopPropagation()}
        >
          {renderRadarContent(true)}
        </div>
      </div>
    )}
  </>
  );
}

function computeScale(
  statKeys: StatAxis[],
  baselineWeakness: TeamWeaknessResponse | null,
  currentWeakness: TeamWeaknessResponse | null
) {
  const values: number[] = [];
  statKeys.forEach(({ key }) => {
    if (baselineWeakness) values.push(baselineWeakness[key]);
    if (currentWeakness) values.push(currentWeakness[key]);
  });
  const baseValues = values.length ? values : [0];
  const minValue = Math.min(...baseValues, -0.5);
  const maxValue = Math.max(...baseValues, 0.5);
  let span = maxValue - minValue;
  if (span < 0.5) span = 0.5;
  const padding = span * 0.15;
  const scaleMin = minValue - padding;
  const scaleMax = maxValue + padding;
  const fullSpan = scaleMax - scaleMin || 1;
  const ringValues = Array.from({ length: DEFAULT_RING_COUNT + 1 }, (_, idx) => {
    return scaleMin + (fullSpan * idx) / DEFAULT_RING_COUNT;
  });
  return { scaleMin, scaleMax, ringValues };
}

function buildPolygonPoints(
  fractions: number[], 
  axisCount: number, 
  radius = RADAR_RADIUS, 
  center = RADAR_CENTER
) {
  return fractions
    .map((fraction, idx) => {
      const { x, y } = getPointForFraction(fraction, idx, axisCount, true, radius, center);
      return `${x},${y}`;
    })
    .join(" ");
}

function buildRingPolygon(
  fraction: number, 
  axisCount: number, 
  radius = RADAR_RADIUS, 
  center = RADAR_CENTER
) {
  return buildPolygonPoints(Array(axisCount).fill(fraction), axisCount, radius, center);
}

function getPointForFraction(
  fraction: number, 
  axisIndex: number, 
  axisCount: number, 
  clampCircle = true,
  radius = RADAR_RADIUS,
  center = RADAR_CENTER
) {
  const angle = getAngle(axisIndex, axisCount);
  const r = clampCircle ? radius * fraction : radius * fraction;
  return {
    x: center.x + r * Math.sin(angle),
    y: center.y - r * Math.cos(angle),
  };
}

function getAngle(axisIndex: number, axisCount: number) {
  return (Math.PI * 2 * axisIndex) / axisCount;
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}