import { useEffect, useState } from "react";
import { PlayerDetail, SeasonStats } from "@/api/players";
import { playerActions } from "@/actions/players";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import StatRow from "@/components/StatRow";
import styles from "./PlayerCard.module.css";

interface PlayerCardProps {
  playerId: number;
  onClose: () => void;
}

export default function PlayerCard({ playerId, onClose }: PlayerCardProps) {
  const [player, setPlayer] = useState<PlayerDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedYear, setSelectedYear] = useState<string>("");

  useEffect(() => {
    const fetchPlayerDetail = async () => {
      setIsLoading(true);
      const result = await playerActions.getPlayerDetail(playerId);
      
      if (result.success && result.data) {
        setPlayer(result.data);
        // Set most recent year as default
        const years = Object.keys(result.data.seasons).sort().reverse();
        if (years.length > 0) {
          setSelectedYear(years[0] || "");
        }
      } else {
        setError(result.error || "Unknown error");
      }
      
      setIsLoading(false);
    };

    fetchPlayerDetail();
  }, [playerId]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const formatStat = (value: number | null | undefined, decimals: number = 3): string => {
    if (value === null || value === undefined) return "N/A";
    return value.toFixed(decimals);
  };

  const renderSeasonStats = (stats: SeasonStats) => {
    return (
      <div className={styles.statsGrid}>
        {/* Basic Stats */}
        <div className={styles.statsSection}>
          <h4>Basic Stats</h4>
          <StatRow label="Games" value={stats.games} />
          <StatRow label="PA" value={stats.plate_appearances} />
          <StatRow label="AB" value={stats.at_bats} />
          <StatRow label="Hits" value={stats.hits} />
          <StatRow label="2B" value={stats.doubles} />
          <StatRow label="3B" value={stats.triples} />
          <StatRow label="HR" value={stats.home_runs} />
          <StatRow label="R" value={stats.runs} />
          <StatRow label="RBI" value={stats.rbi} />
          <StatRow label="BB" value={stats.walks} />
          <StatRow label="SO" value={stats.strikeouts} />
          <StatRow label="SB" value={stats.stolen_bases} />
        </div>

        {/* Rate Stats */}
        <div className={styles.statsSection}>
          <h4>Rate Stats</h4>
          <StatRow label="AVG" value={formatStat(stats.batting_average)} />
          <StatRow label="OBP" value={formatStat(stats.on_base_percentage)} />
          <StatRow label="SLG" value={formatStat(stats.slugging_percentage)} />
          <StatRow label="OPS" value={formatStat(stats.ops)} />
          <StatRow label="ISO" value={formatStat(stats.isolated_power)} />
          <StatRow label="BABIP" value={formatStat(stats.babip)} />
          <StatRow label="BB%" value={formatStat(stats.walk_rate * 100, 1)} suffix="%" />
          <StatRow label="K%" value={formatStat(stats.strikeout_rate * 100, 1)} suffix="%" />
        </div>

        {/* Advanced Stats */}
        <div className={styles.statsSection}>
          <h4>Advanced Stats</h4>
          <StatRow label="wOBA" value={formatStat(stats.woba)} />
          <StatRow label="wRC+" value={formatStat(stats.wrc_plus, 0)} />
          <StatRow label="WAR" value={formatStat(stats.war, 1)} />
          <StatRow label="Off" value={formatStat(stats.off, 1)} />
          <StatRow label="Def" value={formatStat(stats.def_, 1)} />
          <StatRow label="BsR" value={formatStat(stats.base_running, 1)} />
          {stats.hard_hit_rate !== null && stats.hard_hit_rate !== undefined && (
            <StatRow label="Hard Hit%" value={formatStat(stats.hard_hit_rate * 100, 1)} suffix="%" />
          )}
          {stats.barrel_rate !== null && stats.barrel_rate !== undefined && (
            <StatRow label="Barrel%" value={formatStat(stats.barrel_rate * 100, 1)} suffix="%" />
          )}
          {stats.avg_exit_velocity !== null && stats.avg_exit_velocity !== undefined && (
            <StatRow label="Avg EV" value={formatStat(stats.avg_exit_velocity, 1)} suffix=" mph" />
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.dialog}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close player card">
          ×
        </button>

        {isLoading && (
          <div className={styles.loading}>
            <Spinner />
          </div>
        )}

        {error && (
          <div className={styles.error}>
            <p>Error loading player details</p>
            <p className={styles.errorMessage}>{error}</p>
            <Button onClick={onClose} variant="secondary">Close</Button>
          </div>
        )}

        {player && !isLoading && (
          <div className={styles.content}>
            <div className={styles.hero}>
              <div className={styles.portrait}>
                <img
                  src={player.image_url}
                  alt={player.name}
                  onError={(e) => {
                    e.currentTarget.src =
                      "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current";
                  }}
                />
                <span className={styles.badge}>#{player.mlbam_id}</span>
              </div>

              <div className={styles.heroMeta}>
                <div className={styles.titleBlock}>
                  <p className={styles.subtitle}>{player.years_active}</p>
                  <h2 className={styles.playerName}>{player.name}</h2>
                  {player.team_abbrev && (
                    <span className={styles.teamTag}>{player.team_abbrev}</span>
                  )}
                </div>

                <div className={styles.heroStats}>
                  <div className={styles.metric}>
                    <span>Overall Score</span>
                    <strong>
                      {typeof player.overall_score === "number"
                        ? player.overall_score.toFixed(3)
                        : "N/A"}
                    </strong>
                  </div>
                  <div className={styles.metric}>
                    <span>Fangraphs ID</span>
                    <strong>{player.fangraphs_id ?? "N/A"}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.tokens}>
              <div className={styles.token}>
                <span className={styles.tokenLabel}>MLBAM ID</span>
                <span className={styles.tokenValue}>{player.mlbam_id}</span>
              </div>
              <div className={styles.token}>
                <span className={styles.tokenLabel}>FanGraphs ID</span>
                <span className={styles.tokenValue}>{player.fangraphs_id ?? "N/A"}</span>
              </div>
              {player.team_abbrev && (
                <div className={styles.token}>
                  <span className={styles.tokenLabel}>Current Team</span>
                  <span className={styles.tokenValue}>{player.team_abbrev}</span>
                </div>
              )}
            </div>

            <div className={styles.yearSelector}>
              <div>
                <h3>Season Stats</h3>
                <p>Tap a season to review the player&apos;s performance profile.</p>
              </div>
              <div className={styles.yearButtons}>
                {Object.keys(player.seasons).sort().reverse().map((year) => (
                  <button
                    key={year}
                    className={`${styles.yearButton} ${selectedYear === year ? styles.active : ""}`}
                    onClick={() => setSelectedYear(year)}
                  >
                    {year}
                  </button>
                ))}
              </div>
            </div>

            {selectedYear && player.seasons[selectedYear] && (
              <div className={styles.statsContainer}>
                <header className={styles.statsHeader}>
                  <div>
                    <h3>{selectedYear} Season</h3>
                    <p>{player.seasons[selectedYear].team_abbrev || "No team listed"}</p>
                  </div>
                </header>
                {renderSeasonStats(player.seasons[selectedYear])}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
