import styles from "./PercentileRadar.module.css";

type AxisLabelPosition = {
  offsetMultiplier?: number;
  xOffset?: number;
  yOffset?: number;
  anchor?: "start" | "middle" | "end";
};

export type RadarAxisConfig = {
  label: string;
  position?: AxisLabelPosition;
  tooltip?: (value: number) => string;
};

export type PercentileRadarProps = {
  axes: RadarAxisConfig[];
  teamPercentiles: number[];
  leaguePercentiles?: number[];
  baselinePercentile?: number;
  highlightOrder?: number[]; // e.g., [worstIndex, secondWorstIndex]
  className?: string;
  showLegend?: boolean;
  legendItems?: string[];
};

const RING_FRACTIONS = [0.2, 0.4, 0.6, 0.8, 1];
const DEFAULT_BASELINE = 0.5;
const RADAR_SIZE = 320;
const RADAR_CENTER = { x: RADAR_SIZE / 2, y: RADAR_SIZE / 2 };
const RADAR_RADIUS = 120;
const AXIS_LABEL_OFFSET = 1.32;

const DEFAULT_LEGEND = [
  "Percentile vs league (further out = stronger)",
  "Orange fill = league composite, blue = current selection",
  "Dashed ring marks the 50th percentile (league average)"
];

export default function PercentileRadar({
  axes,
  teamPercentiles,
  leaguePercentiles,
  baselinePercentile = DEFAULT_BASELINE,
  highlightOrder = [],
  className,
  showLegend = true,
  legendItems
}: PercentileRadarProps) {
  if (!axes.length) {
    return null;
  }

  const safeTeam = normalizeValues(teamPercentiles, axes.length, baselinePercentile);
  const safeLeague =
    leaguePercentiles && leaguePercentiles.length === axes.length
      ? leaguePercentiles.map(clamp)
      : Array(axes.length).fill(baselinePercentile);

  const ringLabelValues = Array.from(new Set([...RING_FRACTIONS, baselinePercentile])).sort(
    (a, b) => a - b
  );
  const [severeIndex, warnIndex] = highlightOrder;

  return (
    <div className={`${styles.chart} ${className ?? ""}`}>
      <svg
        viewBox={`0 0 ${RADAR_SIZE} ${RADAR_SIZE}`}
        className={styles.svg}
        role="img"
        aria-label="Percentile radar comparison"
      >
        {RING_FRACTIONS.map((fraction) => (
          <polygon
            key={`ring-${fraction}`}
            points={buildRingPolygon(fraction, axes.length)}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="1"
          />
        ))}
        {axes.map((_, idx) => {
          const { x, y } = getPointForFraction(1, idx, axes.length);
          return (
            <line
              key={`axis-line-${idx}`}
              x1={RADAR_CENTER.x}
              y1={RADAR_CENTER.y}
              x2={x}
              y2={y}
              stroke="rgba(255,255,255,0.12)"
              strokeWidth="1"
            />
          );
        })}

        {renderPolygon(safeLeague, axes.length, {
          fill: "rgba(255, 173, 74, 0.18)",
          stroke: "rgba(255, 198, 124, 0.9)",
          strokeWidth: 1.5,
          className: styles.leaguePolygon
        })}

        {renderPolygon(safeTeam, axes.length, {
          fill: "rgba(109,123,255,0.3)",
          stroke: "#6d7bff",
          strokeWidth: 2,
          className: styles.teamPolygon
        })}

        <polygon
          points={buildRingPolygon(baselinePercentile, axes.length)}
          fill="none"
          stroke="rgba(255,255,255,0.35)"
          strokeWidth="1"
          strokeDasharray="6 4"
        />

        {ringLabelValues.map((fraction) => {
          const y =
            RADAR_CENTER.y - RADAR_RADIUS * fraction - (Math.abs(fraction - 1) < 0.0001 ? 12 : 4);
          const isAverage = Math.abs(fraction - baselinePercentile) < 0.0001;
          return (
            <text
              key={`tick-${fraction}`}
              x={RADAR_CENTER.x}
              y={y}
              textAnchor="middle"
              className={`${styles.ringLabel} ${isAverage ? styles.ringLabelAverage : ""}`}
            >
              {formatPercentileTick(fraction)}
              {isAverage ? " (avg)" : ""}
            </text>
          );
        })}

        {axes.map((axis, idx) => {
          const { position } = axis;
          const offsetMultiplier = position?.offsetMultiplier ?? AXIS_LABEL_OFFSET;
          let { x, y } = getPointForFraction(offsetMultiplier, idx, axes.length, false);
          x += position?.xOffset ?? 0;
          y += position?.yOffset ?? 0;

          let anchor: "start" | "end" | "middle";
          if (position?.anchor) {
            anchor = position.anchor;
          } else {
            const cosine = Math.cos(getAngle(idx, axes.length));
            if (Math.abs(cosine) < 0.15) {
              anchor = "middle";
            } else {
              anchor = cosine > 0 ? "start" : "end";
            }
          }

          const labelClass =
            idx === severeIndex
              ? styles.axisLabelSevere
              : idx === warnIndex
              ? styles.axisLabelWarn
              : styles.axisLabel;

          const tooltip = axis.tooltip?.(safeTeam[idx]);

          return (
            <text
              key={`axis-label-${idx}`}
              x={x}
              y={y}
              textAnchor={anchor}
              className={labelClass}
            >
              {axis.label}
              {tooltip ? <title>{tooltip}</title> : null}
            </text>
          );
        })}
      </svg>

      {showLegend && (
        <ul className={styles.legend}>
          {(legendItems ?? DEFAULT_LEGEND).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

type PolygonStyle = {
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  className?: string;
  strokeDasharray?: string;
};

function renderPolygon(fractions: number[], axisCount: number, style?: PolygonStyle) {
  const points = buildPolygonPoints(fractions, axisCount);
  return (
    <polygon
      points={points}
      fill={style?.fill ?? "none"}
      stroke={style?.stroke ?? "#6d7bff"}
      strokeWidth={style?.strokeWidth ?? 2}
      strokeDasharray={style?.strokeDasharray}
      className={style?.className}
    />
  );
}

function buildRingPolygon(fraction: number, axisCount: number) {
  return buildPolygonPoints(Array(axisCount).fill(fraction), axisCount);
}

function buildPolygonPoints(fractions: number[], axisCount: number) {
  return fractions
    .map((fraction, idx) => {
      const { x, y } = getPointForFraction(fraction, idx, axisCount);
      return `${x},${y}`;
    })
    .join(" ");
}

function getPointForFraction(
  fraction: number,
  axisIndex: number,
  axisCount: number,
  clampValue: boolean = true
) {
  const value = clampValue ? clamp(fraction) : fraction;
  const angle = getAngle(axisIndex, axisCount);
  const r = Math.max(value, 0) * RADAR_RADIUS;
  return {
    x: RADAR_CENTER.x + r * Math.cos(angle),
    y: RADAR_CENTER.y + r * Math.sin(angle)
  };
}

function getAngle(axisIndex: number, axisCount: number) {
  return (2 * Math.PI * axisIndex) / axisCount - Math.PI / 2;
}

function normalizeValues(values: number[], targetLength: number, fillValue: number) {
  const normalized = [...values];
  if (normalized.length < targetLength) {
    normalized.push(...Array(targetLength - normalized.length).fill(fillValue));
  }
  if (normalized.length > targetLength) {
    normalized.length = targetLength;
  }
  return normalized.map(clamp);
}

function clamp(value: number) {
  if (!Number.isFinite(value)) {
    return 0;
  }
  if (value < 0) return 0;
  if (value > 1) return 1;
  return value;
}

function formatPercentileTick(value: number) {
  const percentile = Math.round(value * 100);
  return `${percentile}${getOrdinalSuffix(percentile)}`;
}

function getOrdinalSuffix(value: number) {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) {
    return "th";
  }

  switch (value % 10) {
    case 1:
      return "st";
    case 2:
      return "nd";
    case 3:
      return "rd";
    default:
      return "th";
  }
}
