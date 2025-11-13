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
                  <span className={styles.change}>
                    Adj. Score: {player.adjustment_score.toFixed(2)}
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
              <svg viewBox="0 0 280 280" style={{ maxWidth: "280px", width: "100%", height: "auto" }}>
                <polygon points="140,30 210,80 210,200 140,250 70,200 70,80" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <polygon points="140,60 190,95 190,185 140,220 90,185 90,95" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <polygon points="140,90 170,110 170,170 140,190 110,170 110,110" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                {renderRadarPolygon(weakness)}
                <text x="140" y="20" textAnchor="middle" fill="#fff" fontSize="10">Strikeouts</text>
                <text x="225" y="85" textAnchor="start" fill="#fff" fontSize="10">Walk Rate</text>
                <text x="225" y="205" textAnchor="start" fill="#fff" fontSize="10">ISO</text>
                <text x="140" y="270" textAnchor="middle" fill="#fff" fontSize="10">OBP</text>
                <text x="50" y="205" textAnchor="end" fill="#fff" fontSize="10">BsR</text>
                <text x="50" y="85" textAnchor="end" fill="#fff" fontSize="10">K%</text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function renderRadarPolygon(weakness: TeamWeaknessResponse) {
  // Map each stat to a radius (0-1 scaled) and compute polygon points
  const center = { x: 140, y: 140 };
  const radius = 90;
  const stats = [
    weakness.strikeout_rate,
    weakness.walk_rate,
    weakness.isolated_power,
    weakness.on_base_percentage,
    weakness.base_running,
    weakness.strikeout_rate, // close the loop, reuse first
  ];

  const points = stats.map((value, idx) => {
    const angle = (Math.PI / 3) * idx - Math.PI / 2; // hexagon style
    const clamped = Math.min(Math.max(value, 0), 1);
    const r = (clamped * radius) + 20;
    const x = center.x + r * Math.cos(angle);
    const y = center.y + r * Math.sin(angle);
    return `${x},${y}`;
  }).join(" ");

  return <polygon points={points} fill="rgba(109,123,255,0.25)" stroke="#6d7bff" strokeWidth="2" />;
}
