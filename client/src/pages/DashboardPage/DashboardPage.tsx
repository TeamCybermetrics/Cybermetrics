import { useCallback, useEffect, useMemo, useState } from "react";
import Alert from "@/components/Alert";
import PlayerCard from "@/components/PlayerCard";
import { authActions } from "@/actions/auth";
import { healthActions } from "@/actions/health";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import styles from "./DashboardPage.module.css";

type TeamSummary = {
  name: string;
  value: number;
  score: number;
  logo: string;
};

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

const performanceMetrics = [
  { label: "Strikeouts", value: 0.65 },
  { label: "Walk Rate", value: 0.52 },
  { label: "Isolated Power", value: 0.78 },
  { label: "On Base Percent", value: 0.68 },
  { label: "Durability Factor", value: 0.58 },
  { label: "Age", value: 0.62 }
] as const;

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
      if (!query.trim()) {
        setSearchResults([]);
        setIsSearching(false);
        return;
      }

      setIsSearching(true);
      setError("");
      const result = await playerActions.searchPlayers(query);
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
    window.location.href = "/login";
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
              <h1 className={styles.pageTitle}>Dashboard</h1>
              {userEmail && (
                <p className={styles.pageSubtitle}>Signed in as {userEmail}</p>
              )}
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
            <div className={styles.radarWrapper}>
              <svg viewBox="0 0 220 220" className={styles.radarChart} role="presentation">
                {[1, 0.75, 0.5, 0.25].map((ratio) => {
                  const points = performanceMetrics
                    .map((_, index) => {
                      const angle = ((Math.PI * 2) / performanceMetrics.length) * index - Math.PI / 2;
                      const radius = 90 * ratio;
                      const x = 110 + radius * Math.cos(angle);
                      const y = 110 + radius * Math.sin(angle);
                      return `${x},${y}`;
                    })
                    .join(" ");

                  return (
                    <polygon
                      key={ratio}
                      points={points}
                      className={styles.radarGrid}
                    />
                  );
                })}
                {performanceMetrics.map((metric, index) => {
                  const angle =
                    ((Math.PI * 2) / performanceMetrics.length) * index - Math.PI / 2;
                  const x = 110 + 90 * Math.cos(angle);
                  const y = 110 + 90 * Math.sin(angle);
                  return (
                    <line
                      key={metric.label}
                      x1={110}
                      y1={110}
                      x2={x}
                      y2={y}
                      className={styles.radarGrid}
                    />
                  );
                })}

                <polygon
                  className={styles.radarShape}
                  points={performanceMetrics
                    .map((metric, index) => {
                      const angle =
                        ((Math.PI * 2) / performanceMetrics.length) * index - Math.PI / 2;
                      const radius = 90 * metric.value;
                      const x = 110 + radius * Math.cos(angle);
                      const y = 110 + radius * Math.sin(angle);
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />

                {performanceMetrics.map((metric, index) => {
                  const angle =
                    ((Math.PI * 2) / performanceMetrics.length) * index - Math.PI / 2;
                  const radius = 105;
                  const x = 110 + radius * Math.cos(angle);
                  const y = 110 + radius * Math.sin(angle);
                  return (
                    <text
                      key={metric.label}
                      x={x}
                      y={y}
                      className={styles.radarLabel}
                    >
                      {metric.label}
                    </text>
                  );
                })}
              </svg>
            </div>
          </article>
        </div>
      </section>

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

      {selectedPlayerId && (
        <PlayerCard
          playerId={selectedPlayerId}
          onClose={() => setSelectedPlayerId(null)}
        />
      )}
    </div>
  );
}
