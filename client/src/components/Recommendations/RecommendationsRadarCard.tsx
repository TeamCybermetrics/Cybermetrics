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
};

const RADAR_SIZE = 160;
const RADAR_CENTER = { x: RADAR_SIZE / 2, y: RADAR_SIZE / 2 };
const RADAR_RADIUS = 100;
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

export function RecommendationsRadarCard({
  statKeys,
  baselineWeakness,
  currentWeakness,
  highlightOrder,
  loading,
  error,
}: Props) {
  const hasData = !!currentWeakness;

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

  const { scaleMin, scaleMax, ringValues } = computeScale(statKeys, baselineWeakness, currentWeakness);
  const scaleSpan = scaleMax - scaleMin || 1;

  const toFraction = (value: number | undefined | null) => {
    if (value == null || Number.isNaN(value)) return 0.5;
    return clamp((value - scaleMin) / scaleSpan, 0, 1);
  };

  const currentFractions = statKeys.map(({ key }) => toFraction(currentWeakness![key]));
  const baselineFractions = baselineWeakness ? statKeys.map(({ key }) => toFraction(baselineWeakness[key])) : null;

  const ringFractions = ringValues.map((value) => toFraction(value));
  const ringLabels = Array.from(new Set([...ringValues, 0]))
    .sort((a, b) => a - b);

  return (
    <Card title="Before/After" subtitle="Weakness Radar">
      <div className={styles.radarChart}>
        <svg
          viewBox={`${-SVG_PADDING} ${-SVG_PADDING} ${RADAR_SIZE + 2 * SVG_PADDING} ${RADAR_SIZE + 2 * SVG_PADDING}`}
          style={{ width: "100%", maxWidth: "300px", height: "auto", overflow: "visible" }}
        >
          {ringFractions.map((fraction, i) => (
            <polygon
              key={`ring-${i}`}
              points={buildRingPolygon(fraction, statKeys.length)}
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth={1}
            />
          ))}

          {statKeys.map((_, idx) => {
            const { x, y } = getPointForFraction(1, idx, statKeys.length);
            return (
              <line
                key={`axis-${idx}`}
                x1={RADAR_CENTER.x}
                y1={RADAR_CENTER.y}
                x2={x}
                y2={y}
                stroke="rgba(255,255,255,0.12)"
                strokeWidth={1}
              />
            );
          })}

          {baselineFractions && (
            <polygon
              points={buildPolygonPoints(baselineFractions, statKeys.length)}
              className={styles.leaguePolygon}
            />
          )}

          <polygon
            points={buildPolygonPoints(currentFractions, statKeys.length)}
            className={styles.teamPolygon}
          />

          <polygon
            points={buildRingPolygon(toFraction(0), statKeys.length)}
            fill="none"
            stroke="rgba(255,255,255,0.35)"
            strokeWidth={1}
            strokeDasharray="6 4"
          />

          {ringLabels.map((value) => {
            const fraction = toFraction(value);
            const isBaseline = Math.abs(value) < 1e-6;
            const y = RADAR_CENTER.y - RADAR_RADIUS * fraction + (isBaseline ? 6 : -4);
            return (
              <text
                key={`ring-label-${value}`}
                x={RADAR_CENTER.x}
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
          let { x, y } = getPointForFraction(offsetMultiplier, idx, statKeys.length, false);
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
      </div>
      <ul className={styles.radarLegend}>
        <li>Blue = current lineup</li>
        <li>Orange = baseline lineup</li>
        <li>0 = league average; positive = stronger</li>
      </ul>
    </Card>
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

function buildPolygonPoints(fractions: number[], axisCount: number) {
  return fractions
    .map((fraction, idx) => {
      const { x, y } = getPointForFraction(fraction, idx, axisCount);
      return `${x},${y}`;
    })
    .join(" ");
}

function buildRingPolygon(fraction: number, axisCount: number) {
  return buildPolygonPoints(Array(axisCount).fill(fraction), axisCount);
}

function getPointForFraction(fraction: number, axisIndex: number, axisCount: number, clampCircle = true) {
  const angle = getAngle(axisIndex, axisCount);
  const radius = clampCircle ? RADAR_RADIUS * fraction : RADAR_RADIUS * fraction;
  return {
    x: RADAR_CENTER.x + radius * Math.sin(angle),
    y: RADAR_CENTER.y - radius * Math.cos(angle),
  };
}

function getAngle(axisIndex: number, axisCount: number) {
  return (Math.PI * 2 * axisIndex) / axisCount;
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}
