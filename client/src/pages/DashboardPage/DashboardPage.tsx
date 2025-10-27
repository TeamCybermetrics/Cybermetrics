import { useCallback, useEffect, useMemo, useRef, useState, useId } from "react";
import { useNavigate } from "react-router-dom";
import Alert from "@/components/Alert";
import PlayerCard from "@/components/PlayerCard";
import { authActions } from "@/actions/auth";
import { healthActions } from "@/actions/health";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import { ROUTES } from "@/config";
import styles from "./DashboardPage.module.css";

type TeamSummary = {
  name: string;
  value: number;
  score: number;
  logo: string;
};

type RadarMetric = {
  id: string;
  label: string;
  value: number;
  max?: number;
};

type PlayerRadarProfile = Record<RadarMetric["id"], number>;

const DEFAULT_PLAYER_IMAGE =
  "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current";

const sampleTeams: TeamSummary[] = [
  {
    name: "Toronto Blue Jays",
    value: 255_380_936,
    score: 90,
    logo: "https://a.espncdn.com/i/teamlogos/mlb/500/tor.png"
  },
  {
    name: "Los Angeles Dodgers",
    value: 267_227_403,
    score: 88,
    logo: "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png"
  },
  {
    name: "Houston Astros",
    value: 241_867_932,
    score: 84,
    logo: "https://a.espncdn.com/i/teamlogos/mlb/500/hou.png"
  },
  {
    name: "Atlanta Braves",
    value: 238_001_120,
    score: 92,
    logo: "https://a.espncdn.com/i/teamlogos/mlb/500/atl.png"
  },
  {
    name: "New York Yankees",
    value: 300_298_463,
    score: -20,
    logo: "https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png"
  }
];

const BASE_PERFORMANCE_METRICS: RadarMetric[] = [
  { id: "avg", label: "AVG", value: 0.287, max: 0.35 },
  { id: "obp", label: "OBP", value: 0.365, max: 0.45 },
  { id: "slg", label: "SLG", value: 0.512, max: 0.65 },
  { id: "iso", label: "ISO", value: 0.225, max: 0.3 },
  { id: "wrcPlus", label: "wRC+", value: 132, max: 160 }
];

const RADAR_LEVELS = [1, 0.75, 0.5, 0.25];

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

function clamp(value: number, min = 0, max = 1) {
  return Math.min(Math.max(value, min), max);
}

const DEFAULT_PLAYER_PROFILE: PlayerRadarProfile = BASE_PERFORMANCE_METRICS.reduce(
  (acc, metric) => {
    acc[metric.id] = metric.value;
    return acc;
  },
  {} as PlayerRadarProfile
);

const PLAYER_METRIC_LIBRARY: Record<number, PlayerRadarProfile> = {
  660271: {
    avg: 0.304,
    obp: 0.406,
    slg: 0.654,
    iso: 0.350,
    wrcPlus: 180
  },
  665742: {
    avg: 0.289,
    obp: 0.430,
    slg: 0.556,
    iso: 0.267,
    wrcPlus: 164
  },
  660670: {
    avg: 0.337,
    obp: 0.414,
    slg: 0.596,
    iso: 0.259,
    wrcPlus: 170
  },
  608369: {
    avg: 0.327,
    obp: 0.390,
    slg: 0.623,
    iso: 0.296,
    wrcPlus: 169
  }
};

function generateFallbackProfile(player: SavedPlayer, index: number): PlayerRadarProfile {
  const baseSeed = typeof player.id === "number" ? player.id : player.name.length * 31;
  const seed = (baseSeed + index * 29) % 97;

  return BASE_PERFORMANCE_METRICS.reduce((acc, metric, metricIndex) => {
    const max = metric.max ?? 1;
    const base = metric.value;
    const spread = max * 0.3; // up to +/- 30% of the axis max
    const variation = ((seed + metricIndex * 17) % 21 - 10) / 10; // -1..1 step .1
    const adjusted = clamp(base + variation * spread * 0.5, 0, max);
    acc[metric.id] = adjusted;
    return acc;
  }, {} as PlayerRadarProfile);
}

function resolvePlayerProfile(player: SavedPlayer, index: number): PlayerRadarProfile {
  const preset = typeof player.id === "number" ? PLAYER_METRIC_LIBRARY[player.id] : undefined;
  if (preset) {
    return preset;
  }
  return generateFallbackProfile(player, index);
}

function PerformanceRadar({ metrics }: { metrics: RadarMetric[] }) {
  const gradientId = useId();
  const normalized = useMemo(() => {
    if (!metrics.length) {
      return [] as Array<RadarMetric & { normalized: number }>;
    }

    return metrics.map((metric) => {
      const max = metric.max ?? 1;
      const normalizedValue = clamp(max === 0 ? 0 : metric.value / max);
      return {
        ...metric,
        normalized: normalizedValue
      };
    });
  }, [metrics]);

  const targetValues = useMemo(
    () => normalized.map((metric) => metric.normalized),
    [normalized]
  );

  const valuesRef = useRef<number[]>(targetValues);
  const animationRef = useRef<number | null>(null);
  const [displayValues, setDisplayValues] = useState<number[]>(targetValues);

  useEffect(() => {
    if (!targetValues.length) {
      setDisplayValues([]);
      valuesRef.current = [];
      return;
    }

    const previous = valuesRef.current;
    const alignedPrevious = previous.length === targetValues.length
      ? previous
      : targetValues.map(() => 0);

    valuesRef.current = alignedPrevious;

    const unchanged = alignedPrevious.every(
      (value, index) => Math.abs(value - targetValues[index]) < 0.0001
    );

    if (unchanged) {
      return;
    }

    setDisplayValues(alignedPrevious);

    const duration = 650; // ms
    let startTime: number | null = null;

    const animate = (timestamp: number) => {
      if (startTime === null) {
        startTime = timestamp;
      }

      const progress = clamp((timestamp - startTime) / duration, 0, 1);
      const eased = easeOutCubic(progress);

      const nextValues = targetValues.map((target, index) => {
        const starting = alignedPrevious[index] ?? 0;
        return starting + (target - starting) * eased;
      });

      setDisplayValues(nextValues);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        valuesRef.current = targetValues;
        animationRef.current = null;
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [targetValues]);

  if (!normalized.length) {
    return (
      <div className={styles.radarWrapper}>
        <p className={styles.emptyMessage}>No metrics available</p>
      </div>
    );
  }

  const center = 110;
  const radius = 90;
  const angleStep = (Math.PI * 2) / normalized.length;

  const polygonPoints = displayValues
    .map((value, index) => {
      const angle = angleStep * index - Math.PI / 2;
      const r = radius * value;
      const x = center + r * Math.cos(angle);
      const y = center + r * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className={styles.radarWrapper}>
      <svg
        className={styles.radarChart}
        viewBox="0 0 220 220"
        role="img"
        aria-label="Performance radar chart"
      >
        <defs>
          <linearGradient id={gradientId} x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#4d7fff" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#4d7fff" stopOpacity="0.2" />
          </linearGradient>
        </defs>

        {RADAR_LEVELS.map((ratio) => {
          const gridPoints = normalized
            .map((_, index) => {
              const angle = angleStep * index - Math.PI / 2;
              const r = radius * ratio;
              const x = center + r * Math.cos(angle);
              const y = center + r * Math.sin(angle);
              return `${x},${y}`;
            })
            .join(" ");

          return (
            <polygon key={ratio} className={styles.radarGrid} points={gridPoints} />
          );
        })}

        {normalized.map((_, index) => {
          const angle = angleStep * index - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          return (
            <line
              key={`axis-${index}`}
              className={styles.radarGrid}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
            />
          );
        })}

        <polygon
          className={styles.radarShape}
          points={polygonPoints}
          fill={`url(#${gradientId})`}
        />

        {normalized.map((metric, index) => {
          const angle = angleStep * index - Math.PI / 2;
          const labelRadius = radius + 22;
          const x = center + labelRadius * Math.cos(angle);
          const y = center + labelRadius * Math.sin(angle);
          return (
            <text key={metric.id} className={styles.radarLabel} x={x} y={y}>
              {metric.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);

const formatScore = (value: number) => `${value > 0 ? "+" : ""}${value}`;

export default function DashboardPage() {
  const [userEmail, setUserEmail] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [healthStatus, setHealthStatus] = useState("");
  const [healthError, setHealthError] = useState("");
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const navigate = useNavigate();
  const latestQueryRef = useRef("");

  const performanceMetrics = useMemo<RadarMetric[]>(() => {
    if (savedPlayers.length === 0) {
      return BASE_PERFORMANCE_METRICS;
    }

    const profiles = savedPlayers.map((player, index) =>
      resolvePlayerProfile(player, index)
    );

    return BASE_PERFORMANCE_METRICS.map((metric) => {
      const max = metric.max ?? 1;

      const sum = profiles.reduce((acc, profile) => {
        const value = profile[metric.id];
        if (typeof value === "number" && !Number.isNaN(value)) {
          return acc + value;
        }
        return acc + DEFAULT_PLAYER_PROFILE[metric.id];
      }, 0);

      const average = sum / profiles.length;

      return {
        ...metric,
        value: clamp(average, 0, max)
      };
    });
  }, [savedPlayers]);

  useEffect(() => {
    const user = authActions.getCurrentUser();
    if (user.email) {
      setUserEmail(user.email);
    }
    void refreshSavedPlayers();
  }, []);

  const refreshSavedPlayers = async () => {
    const result = await playerActions.getSavedPlayers();
    if (result.success && result.data) {
      setSavedPlayers(result.data);
    }
  };

  const performSearch = useCallback(
    async (query: string) => {
      const trimmed = query.trim();

      if (!trimmed) {
        latestQueryRef.current = "";
        setSearchResults([]);
        setIsSearching(false);
        setError("");
        return;
      }

      setIsSearching(true);
      setError("");
      const result = await playerActions.searchPlayers(trimmed);

      if (latestQueryRef.current !== trimmed) {
        return;
      }

      setIsSearching(false);

      if (result.success && result.data) {
        setSearchResults(result.data);
      } else {
        setError(result.error || "Search failed");
        setSearchResults([]);
      }
    },
    []
  );

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      latestQueryRef.current = searchQuery.trim();
      void performSearch(searchQuery);
    }, 250);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, performSearch]);

  const handleAddPlayer = async (player: PlayerSearchResult) => {
    setError("");
    setSuccess("");

    const result = await playerActions.addPlayer({
      id: player.id,
      name: player.name,
      image_url: player.image_url,
      years_active: player.years_active
    });

    if (result.success) {
      setSuccess(`Added ${player.name} to saved players`);
      await refreshSavedPlayers();
      setTimeout(() => setSuccess(""), 2400);
    } else {
      setError(result.error || "Failed to add player");
    }
  };

  const handleDeletePlayer = async (player: SavedPlayer) => {
    setError("");
    setSuccess("");

    const result = await playerActions.deletePlayer(player.id);

    if (result.success) {
      setSuccess(`Removed ${player.name} from saved players`);
      await refreshSavedPlayers();
      setTimeout(() => setSuccess(""), 2400);
    } else {
      setError(result.error || "Failed to remove player");
    }
  };

  const handleLogout = () => {
    authActions.logout();
    navigate(ROUTES.LOGIN);
  };

  const handleCheckHealth = async () => {
    setIsCheckingHealth(true);
    setHealthStatus("");
    setHealthError("");

    const result = await healthActions.checkHealth();

    if (result.success) {
      const status = result.data.status;
      const firebaseStatus = result.data.firebase_connected ? "connected" : "disconnected";
      setHealthStatus(`Server is ${status}, Firebase is ${firebaseStatus}`);
    } else {
      setHealthError(result.error);
    }

    setIsCheckingHealth(false);
  };

  const teamBudget = useMemo(() => {
    if (savedPlayers.length === 0) {
      return 153_460_346;
    }

    return savedPlayers.reduce(
      (acc, player, index) =>
        acc + ((typeof player.contract_value === "number" && player.contract_value > 0)
          ? player.contract_value
          : 18_000_000 + index * 2_750_000),
      0
    );
  }, [savedPlayers]);

  const teamScore = useMemo(() => {
    if (savedPlayers.length === 0) {
      return 130;
    }

    const aggregate = savedPlayers.reduce((acc, player) => {
      const playerScore =
        typeof player.score === "number"
          ? player.score
          : typeof player.overall_score === "number"
          ? player.overall_score
          : 88;
      return acc + playerScore;
    }, 0);

    return Math.round(aggregate / savedPlayers.length);
  }, [savedPlayers]);

  const targetWeakness = useMemo(() => {
    if (savedPlayers.length >= 9) return "Bullpen Velocity";
    if (savedPlayers.length >= 5) return "Strikeout Rate";
    return "Roster Depth";
  }, [savedPlayers.length]);

  const extendedTeamList = useMemo(() => {
    if (savedPlayers.length === 0) {
      return sampleTeams;
    }

    return savedPlayers.slice(0, 5).map((player, index, list) => {
      const value = 225_000_000 + index * 3_500_000;
      const isLastEntry = index === list.length - 1 && list.length > 3;
      const score = isLastEntry ? -20 : 94 - index * 4;

      return {
        name: player.name,
        value,
        score,
        logo: player.image_url || DEFAULT_PLAYER_IMAGE
      };
    });
  }, [savedPlayers]);

  const closeSearchPanel = () => {
    setIsSearchOpen(false);
    setSearchQuery("");
    setSearchResults([]);
  };

  return (
    <div className={styles.page}>
      <header className={styles.pageHeader}>
        <div>
          <h1 className={styles.pageTitle}>Dashboard</h1>
          <p className={styles.pageSubtitle}>Track your roster and scouting insights.</p>
        </div>
        {userEmail && <span className={styles.pageMeta}>Signed in as {userEmail}</span>}
      </header>

      <div className={styles.dashboard}>
        <section className={styles.lineupPanel}>
          <header className={styles.lineupHeader}>
            <div>
              <h2 className={styles.lineupTitle}>Current Lineup</h2>
              <p className={styles.lineupHint}>Monitor the roster you&apos;re tracking.</p>
            </div>
            <button
              className={styles.lineupAction}
              type="button"
              onClick={() => setIsSearchOpen(true)}
            >
              Add Players
            </button>
          </header>

          <div className={styles.lineupList}>
            {savedPlayers.length === 0 ? (
              <div className={styles.lineupEmpty}>
                <p className={styles.emptyTitle}>No players saved yet</p>
                <p className={styles.emptyHint}>Use “Add Players” to start building your lineup.</p>
                <button
                  className={styles.emptyButton}
                  type="button"
                  onClick={() => setIsSearchOpen(true)}
                >
                  Scout Players
                </button>
              </div>
            ) : (
              savedPlayers.map((player) => (
                <article key={player.id} className={styles.lineupItem}>
                  <button
                    type="button"
                    className={styles.lineupProfile}
                    onClick={() => setSelectedPlayerId(player.id)}
                  >
                    <img
                      src={player.image_url || DEFAULT_PLAYER_IMAGE}
                      alt={player.name}
                      onError={(e) => {
                        e.currentTarget.src = DEFAULT_PLAYER_IMAGE;
                      }}
                    />
                    <div className={styles.lineupInfo}>
                      <span className={styles.playerName}>{player.name}</span>
                      <span className={styles.playerMeta}>
                        {player.team ?? player.years_active ?? "Scouting target"}
                      </span>
                    </div>
                  </button>
                  <button
                    type="button"
                    className={styles.lineupRemove}
                    onClick={() => handleDeletePlayer(player)}
                  >
                    Remove
                  </button>
                </article>
              ))
            )}
          </div>

          <footer className={styles.lineupFooter}>
            <button
              type="button"
              className={styles.footerButton}
              onClick={() => setIsSearchOpen(true)}
            >
              View All
            </button>
          </footer>
        </section>

        <section className={styles.analytics}>
          <article className={styles.statsCard}>
            <header className={styles.statsHeader}>
              <div>
                <h2 className={styles.statsTitle}>Team Snapshot</h2>
                <p className={styles.statsSubtitle}>Budget, score, and focus areas.</p>
              </div>
              <div className={styles.statsActions}>
                <button
                  className={styles.utilityButton}
                  type="button"
                  onClick={handleCheckHealth}
                  disabled={isCheckingHealth}
                >
                  {isCheckingHealth ? "Checking..." : "Check Health"}
                </button>
                <button
                  className={styles.utilityButton}
                  type="button"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </header>

            <div className={styles.statBlocks}>
              <div className={styles.statBlock}>
                <p className={styles.statLabel}>Team Budget</p>
                <p className={styles.statValue}>{formatCurrency(teamBudget)}</p>
              </div>
              <div className={styles.statBlock}>
                <p className={styles.statLabel}>Team Score</p>
                <p className={`${styles.statValue} ${styles.positive}`}>
                  {formatScore(teamScore)}
                </p>
              </div>
              <div className={styles.statBlock}>
                <p className={styles.statLabel}>Target Weakness</p>
                <p className={styles.statValue}>{targetWeakness}</p>
              </div>
            </div>
          </article>

          <div className={styles.lowerGrid}>
            <article className={styles.teamsCard}>
              <header className={styles.cardHeader}>
                <h3>MLB Teams</h3>
                <button type="button" className={styles.headerLink}>
                  View All
                </button>
              </header>
              <div className={styles.teamTable}>
                <div className={styles.teamHeadings}>
                  <span>Team</span>
                  <span>Team Score</span>
                </div>
                <ul>
                  {extendedTeamList.map((team) => (
                    <li key={team.name} className={styles.teamRow}>
                      <div className={styles.teamMeta}>
                        <img src={team.logo} alt={team.name} />
                        <div>
                          <p className={styles.teamName}>{team.name}</p>
                          <span className={styles.teamValue}>{formatCurrency(team.value)}</span>
                        </div>
                      </div>
                      <span
                        className={
                          team.score >= 0 ? styles.teamScorePositive : styles.teamScoreNegative
                        }
                      >
                        {formatScore(team.score)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </article>

            <article className={styles.performanceCard}>
              <header className={styles.cardHeader}>
                <h3>Performance</h3>
              </header>
              <PerformanceRadar metrics={performanceMetrics} />
          </article>
        </div>
      </section>
      </div>

      {isSearchOpen && (
        <div className={styles.searchOverlay}>
          <div className={styles.searchCard}>
            <header className={styles.searchHeader}>
              <div>
                <h3>Scout Players</h3>
                <p>Search the database and add prospects to your lineup.</p>
              </div>
              <button type="button" className={styles.closeButton} onClick={closeSearchPanel}>
                Close
              </button>
            </header>

            <div className={styles.searchBody}>
              <div className={styles.searchFieldWrapper}>
                <input
                  className={styles.searchField}
                  type="text"
                  placeholder="Start typing to search for a player..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {isSearching && <span className={styles.searchStatus}>Searching…</span>}
              </div>

              {searchResults.length > 0 && (
                <ul className={styles.resultsList}>
                  {searchResults.map((player) => (
                    <li key={player.id} className={styles.resultRow}>
                      <button
                        type="button"
                        className={styles.resultProfile}
                        onClick={() => setSelectedPlayerId(player.id)}
                      >
                        <img
                          src={player.image_url || DEFAULT_PLAYER_IMAGE}
                          alt={player.name}
                          onError={(e) => {
                            e.currentTarget.src = DEFAULT_PLAYER_IMAGE;
                          }}
                        />
                        <div>
                          <p className={styles.playerName}>{player.name}</p>
                          <span className={styles.playerMeta}>{player.years_active}</span>
                          <span className={styles.playerId}>ID: {player.id}</span>
                        </div>
                      </button>
                      <button
                        type="button"
                        className={styles.addButton}
                        onClick={() => handleAddPlayer(player)}
                      >
                        Add
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {searchQuery && !isSearching && searchResults.length === 0 && (
                <p className={styles.emptyCopy}>
                  No players found matching “{searchQuery}”.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {(success || error || healthStatus || healthError) && (
        <div className={styles.feedback}>
          {success && <Alert type="success">{success}</Alert>}
          {error && <Alert type="error">{error}</Alert>}
          {healthStatus && <Alert type="success">{healthStatus}</Alert>}
          {healthError && <Alert type="error">{healthError}</Alert>}
        </div>
      )}

      {selectedPlayerId !== null && (
        <PlayerCard
          playerId={selectedPlayerId}
          onClose={() => setSelectedPlayerId(null)}
        />
      )}
    </div>
  );
}
