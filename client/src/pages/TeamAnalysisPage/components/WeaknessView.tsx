import type { PlayerValueScore, TeamWeaknessResponse } from "@/api/players";
import { Card, CardGrid } from "@/components";
import styles from "./WeaknessView.module.css";

type PlayerScoreCard = PlayerValueScore & {
  image_url?: string;
  years_active?: string;
};

type WeaknessViewProps = {
  weakness: TeamWeaknessResponse | null;
  players: PlayerScoreCard[];
  loading: boolean;
  error: string | null;
  hasRoster: boolean;
  onRetry: () => void;
};

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

export default function WeaknessView({
  weakness,
  players,
  loading,
  error,
  hasRoster,
  onRetry
}: WeaknessViewProps) {
  if (!hasRoster) {
    return <div className={styles.stateMessage}>Add saved players to your roster to view weaknesses.</div>;
  }

  if (loading) {
    return <div className={styles.stateMessage}>Analyzing lineup…</div>;
  }

  if (error) {
    return (
      <div className={styles.stateError}>
        <span>{error}</span>
        <button className={styles.retryButton} onClick={onRetry}>Retry</button>
      </div>
    );
  }

  if (!weakness) {
    return <div className={styles.stateMessage}>Unable to compute weaknesses.</div>;
  }

  const percentileFractions = getValueFractions(weakness);
  const rankedAxes = percentileFractions
    .map((value, idx) => ({ value, idx }))
    .sort((a, b) => a.value - b.value);
  const worstAxisIndex = rankedAxes[0]?.idx ?? null;
  const secondWorstAxisIndex = rankedAxes[1]?.idx ?? null;
  const leagueBaselinePolygon = Array(STAT_LABELS.length).fill(BASELINE_FRACTION);

  return (
    <div className={styles.container}>
      <Card title="Team Stats" subtitle="Your lineup compared to league averages">
        <div className={styles.statsRow}>
          {STAT_LABELS.map(({ key, label }) => {
            const rawValue = weakness[key];
            return (
              <div key={key} className={styles.statBlock}>
                <div className={styles.statLabel}>{label}</div>
                <div className={styles.statValue}>{formatValueLabel(rawValue)}</div>
              </div>
            );
          })}
        </div>
      </Card>

      <CardGrid columns={2} gap="large">
        <Card title="Player Adjustment Scores" subtitle="How each player addresses team weaknesses">
          {players.length === 0 ? (
            <div className={styles.stateMessage}>No player metrics available.</div>
          ) : (
            <div className={styles.playerList}>
              {players.map((player) => (
                <div key={player.id} className={styles.playerCard}>
                  <img
                    src={player.image_url || "https://via.placeholder.com/50"}
                    alt={player.name}
                    className={styles.avatar}
                  />
                  <span className={styles.playerName}>{player.name}</span>
                  <span className={styles.playerMeta}>{player.years_active || ""}</span>
                  <span
                    className={
                      player.adjustment_score >= 0 ? styles.scorePositive : styles.scoreNegative
                    }
                  >
                    Adj. Score: {player.adjustment_score >= 0 ? "+" : ""}
                    {player.adjustment_score.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Weakness Radar" subtitle="Visual comparison of your team's performance">
          <div className={styles.radarChart}>
              <svg
                viewBox={`0 0 ${RADAR_SIZE} ${RADAR_SIZE}`}
                style={{ maxWidth: "320px", width: "100%", height: "auto", overflow: "visible" }}
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
                })}
                {/* team polygon */}
                {renderRadarPolygon(percentileFractions, {
                  fill: "rgba(109,123,255,0.3)",
                  stroke: "#6d7bff",
                  strokeWidth: 2,
                  className: styles.teamPolygon
                })}
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
                      className={`${styles.ringLabel} ${isBaseline ? styles.ringLabelAverage : ""}`}
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
                  const rawValue = weakness[axis.key];
                  let labelClass = styles.axisLabel;
                  if (idx === worstAxisIndex) labelClass = styles.axisLabelSevere; else if (idx === secondWorstAxisIndex) labelClass = styles.axisLabelWarn;
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
          <ul className={styles.radarLegend}>
            <li>Score: Number of standard deviations above or below the mean</li>
            <li>Dashed ring marks score 0 (league average baseline)</li>
            <li>Orange fill = league composite, blue = your lineup</li>
            <li>Only the two weakest axes highlight in color</li>
          </ul>
        </Card>
      </CardGrid>
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

function renderRadarPolygon(fractions: number[], style?: PolygonStyle) {
  const points = buildPolygonPoints(fractions);

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

function getAngle(axisIndex: number) {
  return (2 * Math.PI * axisIndex) / STAT_LABELS.length - Math.PI / 2;
}

function getPointForFraction(fraction: number, axisIndex: number, clamp: boolean = true) {
  const value = clamp ? Math.min(Math.max(fraction, 0), 1) : fraction;
  const angle = getAngle(axisIndex);
  const r = Math.max(value, 0) * RADAR_RADIUS;
  return {
    x: RADAR_CENTER.x + r * Math.cos(angle),
    y: RADAR_CENTER.y + r * Math.sin(angle),
  };
}

function buildPolygonPoints(fractions: number[]) {
  return fractions
    .map((fraction, idx) => {
      const { x, y } = getPointForFraction(fraction, idx);
      return `${x},${y}`;
    })
    .join(" ");
}

function buildRingPolygon(fraction: number) {
  return buildPolygonPoints(Array(STAT_LABELS.length).fill(fraction));
}

function weaknessToValue(value: number) {
  if (!Number.isFinite(value)) return BASELINE_VALUE;
  return Number(value.toPrecision(3));
}

function getValueFractions(weakness: TeamWeaknessResponse) {
  return STAT_LABELS.map(({ key }) => valueToFraction(weaknessToValue(weakness[key])));
}

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

function formatValueLabel(value: number) {
  return `${formatValueNumber(value)}`;
}

function formatValueTick(value: number) {
  return `${formatValueNumber(value)}`;
}

function formatValueNumber(value: number) {
  if (!Number.isFinite(value)) return "-";
  return (value >= 0 ? "+" : "") + value.toFixed(2).replace(/\.00$/, "");
}
