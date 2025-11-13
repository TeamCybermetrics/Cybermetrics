import type { PlayerValueScore, TeamWeaknessResponse } from "@/api/players";
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

const STAT_LABELS: { key: keyof TeamWeaknessResponse; label: string }[] = [
  { key: "strikeout_rate", label: "Strikeout Rate" },
  { key: "walk_rate", label: "Walk Rate" },
  { key: "isolated_power", label: "Iso Power" },
  { key: "on_base_percentage", label: "On Base %" },
  { key: "base_running", label: "Base Running" }
];

const RING_FRACTIONS = [0.25, 0.5, 0.75, 1];
const RADAR_SIZE = 320;
const RADAR_CENTER = { x: RADAR_SIZE / 2, y: RADAR_SIZE / 2 };
const RADAR_RADIUS = 120;
const AXIS_LABEL_OFFSET = 1.32;
const LEFT_AXIS_PADDING = 14;
const RIGHT_AXIS_PADDING = 22;
const BASE_AXIS_VERTICAL_OFFSET = 6;

const formatPercent = (value: number) => `${Math.round(value * 100)}%`;

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

  return (
    <div className={styles.container}>
      <div className={styles.statsBubble}>
        <div className={styles.statsHeader}>Team Weakness</div>
        <div className={styles.statsRow}>
          {STAT_LABELS.map(({ key, label }) => (
            <div key={key} className={styles.statBlock}>
              <div className={styles.statLabel}>{label}</div>
              <div className={styles.statValue}>
                {formatPercent(Math.max(0, weakness[key]))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.leftColumn}>
          <h2 className={styles.sectionTitle}>Player adjustment scores</h2>
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
        </div>

        <div className={styles.radarSection}>
          <div className={styles.radarCard}>
            <div className={styles.radarLabel}>Weakness radar</div>
            <div className={styles.radarChart}>
              <svg
                viewBox={`0 0 ${RADAR_SIZE} ${RADAR_SIZE}`}
                style={{ maxWidth: "320px", width: "100%", height: "auto", overflow: "visible" }}
              >
                {/* rings */}
                {RING_FRACTIONS.map((fraction) => (
                  <polygon
                    key={fraction}
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
                {/* ring labels */}
                {RING_FRACTIONS.map((fraction, idx) => (
                  <text
                    key={`label-${fraction}`}
                    x={RADAR_CENTER.x}
                    y={RADAR_CENTER.y - RADAR_RADIUS * fraction - (idx === RING_FRACTIONS.length - 1 ? 12 : 6)}
                    textAnchor="middle"
                    className={styles.ringLabel}
                  >
                    {formatPercent(fraction)}
                  </text>
                ))}
                {/* axis labels */}
                {STAT_LABELS.map((axis, idx) => {
                  let { x, y } = getPointForFraction(AXIS_LABEL_OFFSET, idx, false);
                  let anchor: "start" | "end" | "middle";
                  const cosine = Math.cos(getAngle(idx));
                  if (idx === 4) {
                    x -= LEFT_AXIS_PADDING;
                    y += BASE_AXIS_VERTICAL_OFFSET;
                    anchor = "end";
                  } else if (idx === 1) {
                    x -= RIGHT_AXIS_PADDING;
                    anchor = "start";
                  } else if (Math.abs(cosine) < 0.15) {
                    anchor = "middle";
                  } else {
                    anchor = cosine > 0 ? "start" : "end";
                  }
                  const axisValue = weakness[axis.key];
                  const labelClass =
                    axisValue >= 0.75
                      ? styles.axisLabelSevere
                      : axisValue >= 0.5
                      ? styles.axisLabelWarn
                      : styles.axisLabel;

                  return (
                    <text
                      key={`axis-label-${axis.key}`}
                      x={x}
                      y={y}
                      textAnchor={anchor}
                      className={labelClass}
                    >
                      {axis.label}
                      <title>{`${axis.label}: ${formatPercent(axisValue)} weakness`}</title>
                    </text>
                  );
                })}
                {renderRadarPolygon(weakness)}
              </svg>
            </div>
            <ul className={styles.radarLegend}>
              <li>0% = on par with the league</li>
              <li>100% = largest deficit observed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function renderRadarPolygon(weakness: TeamWeaknessResponse) {
  const fractions = STAT_LABELS.map(({ key }) =>
    Math.min(Math.max(weakness[key], 0), 1)
  );

  const points = buildPolygonPoints(fractions);

  return (
    <polygon
      points={points}
      fill="rgba(109,123,255,0.25)"
      stroke="#6d7bff"
      strokeWidth="2"
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
