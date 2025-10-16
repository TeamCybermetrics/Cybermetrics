import { useEffect, useState } from "react";
import { PlayerDetail, SeasonStats } from "@/api/players";
import { playerActions } from "@/actions/players";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
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
          <div className={styles.statRow}>
            <span>Games:</span> <strong>{stats.games}</strong>
          </div>
          <div className={styles.statRow}>
            <span>PA:</span> <strong>{stats.plate_appearances}</strong>
          </div>
          <div className={styles.statRow}>
            <span>AB:</span> <strong>{stats.at_bats}</strong>
          </div>
          <div className={styles.statRow}>
            <span>Hits:</span> <strong>{stats.hits}</strong>
          </div>
          <div className={styles.statRow}>
            <span>2B:</span> <strong>{stats.doubles}</strong>
          </div>
          <div className={styles.statRow}>
            <span>3B:</span> <strong>{stats.triples}</strong>
          </div>
          <div className={styles.statRow}>
            <span>HR:</span> <strong>{stats.home_runs}</strong>
          </div>
          <div className={styles.statRow}>
            <span>R:</span> <strong>{stats.runs}</strong>
          </div>
          <div className={styles.statRow}>
            <span>RBI:</span> <strong>{stats.rbi}</strong>
          </div>
          <div className={styles.statRow}>
            <span>BB:</span> <strong>{stats.walks}</strong>
          </div>
          <div className={styles.statRow}>
            <span>SO:</span> <strong>{stats.strikeouts}</strong>
          </div>
          <div className={styles.statRow}>
            <span>SB:</span> <strong>{stats.stolen_bases}</strong>
          </div>
        </div>

        {/* Rate Stats */}
        <div className={styles.statsSection}>
          <h4>Rate Stats</h4>
          <div className={styles.statRow}>
            <span>AVG:</span> <strong>{formatStat(stats.batting_average)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>OBP:</span> <strong>{formatStat(stats.on_base_percentage)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>SLG:</span> <strong>{formatStat(stats.slugging_percentage)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>OPS:</span> <strong>{formatStat(stats.ops)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>ISO:</span> <strong>{formatStat(stats.isolated_power)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>BABIP:</span> <strong>{formatStat(stats.babip)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>BB%:</span> <strong>{formatStat(stats.walk_rate * 100, 1)}%</strong>
          </div>
          <div className={styles.statRow}>
            <span>K%:</span> <strong>{formatStat(stats.strikeout_rate * 100, 1)}%</strong>
          </div>
        </div>

        {/* Advanced Stats */}
        <div className={styles.statsSection}>
          <h4>Advanced Stats</h4>
          <div className={styles.statRow}>
            <span>wOBA:</span> <strong>{formatStat(stats.woba)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>wRC+:</span> <strong>{formatStat(stats.wrc_plus, 0)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>WAR:</span> <strong>{formatStat(stats.war, 1)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>Off:</span> <strong>{formatStat(stats.off, 1)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>Def:</span> <strong>{formatStat(stats.def_, 1)}</strong>
          </div>
          <div className={styles.statRow}>
            <span>BsR:</span> <strong>{formatStat(stats.base_running, 1)}</strong>
          </div>
          {stats.hard_hit_rate !== null && stats.hard_hit_rate !== undefined && (
            <div className={styles.statRow}>
              <span>Hard Hit%:</span> <strong>{formatStat(stats.hard_hit_rate * 100, 1)}%</strong>
            </div>
          )}
          {stats.barrel_rate !== null && stats.barrel_rate !== undefined && (
            <div className={styles.statRow}>
              <span>Barrel%:</span> <strong>{formatStat(stats.barrel_rate * 100, 1)}%</strong>
            </div>
          )}
          {stats.avg_exit_velocity !== null && stats.avg_exit_velocity !== undefined && (
            <div className={styles.statRow}>
              <span>Avg EV:</span> <strong>{formatStat(stats.avg_exit_velocity, 1)} mph</strong>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.modal}>
        <button className={styles.closeButton} onClick={onClose}>
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
            <div className={styles.header}>
              <img
                src={player.image_url}
                alt={player.name}
                className={styles.playerImage}
                onError={(e) => {
                  e.currentTarget.src = 'https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current';
                }}
              />
              <div className={styles.headerInfo}>
                <h2 className={styles.playerName}>{player.name}</h2>
                <p className={styles.yearsActive}>{player.years_active}</p>
                {player.team_abbrev && <p className={styles.team}>{player.team_abbrev}</p>}
                <p className={styles.overallScore}>Overall Score: {player.overall_score.toFixed(3)}</p>
              </div>
            </div>

            <div className={styles.details}>
              <div className={styles.detailRow}>
                <span className={styles.label}>MLBAM ID:</span>
                <span className={styles.value}>{player.mlbam_id}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>FanGraphs ID:</span>
                <span className={styles.value}>{player.fangraphs_id}</span>
              </div>
            </div>

            {/* Year Selector */}
            <div className={styles.yearSelector}>
              <h3>Season Stats</h3>
              <div className={styles.yearButtons}>
                {Object.keys(player.seasons).sort().reverse().map((year) => (
                  <button
                    key={year}
                    className={`${styles.yearButton} ${selectedYear === year ? styles.active : ''}`}
                    onClick={() => setSelectedYear(year)}
                  >
                    {year}
                  </button>
                ))}
              </div>
            </div>

            {/* Stats Display */}
            {selectedYear && player.seasons[selectedYear] && (
              <div className={styles.statsContainer}>
                <h3>{selectedYear} Season - {player.seasons[selectedYear].team_abbrev || 'N/A'}</h3>
                {renderSeasonStats(player.seasons[selectedYear])}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

