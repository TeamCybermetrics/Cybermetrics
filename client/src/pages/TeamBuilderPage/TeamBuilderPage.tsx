import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent } from "react";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import styles from "./TeamBuilderPage.module.css";

type DiamondPosition = "LF" | "CF" | "RF" | "3B" | "SS" | "2B" | "1B" | "C" | "DH";

type SavedTeam = {
  id: string;
  name: string;
  lineup: LineupState;
  savedAt: string;
};

const DEFAULT_PLAYER_IMAGE =
  "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current";

const positionOrder: DiamondPosition[] = ["LF", "CF", "RF", "3B", "SS", "2B", "1B", "C", "DH"];

const positionCoordinates: Record<DiamondPosition, { top: string; left: string }> = {
  LF: { top: "16%", left: "13%" },
  CF: { top: "8%", left: "50%" },
  RF: { top: "16%", left: "87%" },
  SS: { top: "38%", left: "32%" },
  "2B": { top: "38%", left: "68%" },
  "3B": { top: "56%", left: "18%" },
  "1B": { top: "56%", left: "82%" },
  C: { top: "75%", left: "50%" },
  DH: { top: "82%", left: "80%" }
};

const staticSpots = [
  {
    label: "P",
    top: "48%",
    left: "50%"
  }
];

type LineupState = Record<DiamondPosition, SavedPlayer | null>;

/**
 * Interactive team builder page that lets users search and manage players, construct a lineup using click or drag-and-drop, apply filters, and save or load teams to localStorage.
 *
 * @returns The React element rendering the Team Builder page.
 */
export default function TeamBuilderPage() {
  const [lineup, setLineup] = useState<LineupState>(() =>
    positionOrder.reduce((acc, position) => ({ ...acc, [position]: null }), {} as LineupState)
  );
  const [activePosition, setActivePosition] = useState<DiamondPosition | null>("CF");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const searchControllerRef = useRef<AbortController | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [teamName, setTeamName] = useState("TeamName1");
  const [isEditingTeamName, setIsEditingTeamName] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [loadTeamOpen, setLoadTeamOpen] = useState(false);
  const [savedTeams, setSavedTeams] = useState<SavedTeam[]>([]);
  const [salaryRange, setSalaryRange] = useState<[number, number]>([0, 100000000]);
  const [selectedPositions, setSelectedPositions] = useState<Set<string>>(new Set(positionOrder));
  const [recommendedPlayers, setRecommendedPlayers] = useState<PlayerSearchResult[]>([]);
  const [recommendationError, setRecommendationError] = useState("");
  const [isRecommending, setIsRecommending] = useState(false);

  // Load saved teams from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("savedTeams");
    if (stored) {
      try {
        setSavedTeams(JSON.parse(stored));
      } catch (e) {
        console.error("Failed to load saved teams:", e);
      }
    }
  }, []);

  // Load saved players on mount
  useEffect(() => {
    const fetchSaved = async () => {
      const result = await playerActions.getSavedPlayers();
      if (result.success && result.data) {
        setSavedPlayers(result.data);
      }
    };

    void fetchSaved();
  }, []);

  const performSearch = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) {
      searchControllerRef.current?.abort();
      searchControllerRef.current = null;
      setSearchResults([]);
      return;
    }

    searchControllerRef.current?.abort();
    const controller = new AbortController();
    searchControllerRef.current = controller;

    const result = await playerActions.searchPlayers(trimmed, controller.signal);

    if (searchControllerRef.current !== controller) {
      return;
    }

    if (result.success && result.data) {
      setSearchResults(result.data);
      searchControllerRef.current = null;
      return;
    }

    if (result.aborted) {
      searchControllerRef.current = null;
      return;
    }

    setSearchResults([]);
    searchControllerRef.current = null;
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      void performSearch(searchTerm);
    }, 250);

    return () => clearTimeout(timer);
  }, [performSearch, searchTerm]);

  useEffect(() => {
    return () => {
      searchControllerRef.current?.abort();
    };
  }, []);

  const availablePlayers = useMemo(() => {
    if (searchTerm.trim()) {
      return searchResults.map((result) => ({
        id: result.id,
        name: result.name,
        image_url: result.image_url,
        years_active: result.years_active
      })) as SavedPlayer[];
    }
    return savedPlayers;
  }, [searchResults, searchTerm, savedPlayers]);

  const assignPlayerToPosition = useCallback((player: SavedPlayer, position: DiamondPosition) => {
    setLineup((prev) => {
      const next: LineupState = { ...prev };

      positionOrder.forEach((slot) => {
        if (next[slot]?.id === player.id) {
          next[slot] = null;
        }
      });

      next[position] = player;
      return next;
    });

    setActivePosition(position);
  }, []);

  const handleClearSlot = (position: DiamondPosition) => {
    setLineup((prev) => ({
      ...prev,
      [position]: null
    }));
  };

  const assignedIds = useMemo(
    () =>
      new Set(
        positionOrder
          .map((pos) => lineup[pos]?.id)
          .filter((id): id is number => typeof id === "number")
      ),
    [lineup]
  );

  const incompletePositions = useMemo(
    () => positionOrder.filter((position) => !lineup[position]),
    [lineup]
  );

  const isRosterComplete = incompletePositions.length === 0;

  const prepareDragPlayer = (player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = { ...player };
    setDraggingId(player.id);
    if (fromPosition) {
      setActivePosition(fromPosition);
    }
  };

  const clearDragState = () => {
    dragPlayerRef.current = null;
    setDropTarget(null);
    setDraggingId(null);
  };

  const handlePositionDrop = (event: DragEvent<HTMLButtonElement>, position: DiamondPosition) => {
    event.preventDefault();
    event.stopPropagation();
    const player = dragPlayerRef.current;
    if (!player) {
      clearDragState();
      return;
    }

    assignPlayerToPosition(player, position);
    clearDragState();
  };

  const saveTeam = () => {
    const newTeam: SavedTeam = {
      id: Date.now().toString(),
      name: teamName,
      lineup: lineup,
      savedAt: new Date().toISOString()
    };

    const updatedTeams = [...savedTeams, newTeam];
    setSavedTeams(updatedTeams);
    localStorage.setItem("savedTeams", JSON.stringify(updatedTeams));
    alert(`Team "${teamName}" saved successfully!`);
  };

  const loadTeam = (team: SavedTeam) => {
    setTeamName(team.name);
    setLineup(team.lineup);
    setLoadTeamOpen(false);
    alert(`Team "${team.name}" loaded!`);
  };

  const deleteTeam = (teamId: string) => {
    const updatedTeams = savedTeams.filter((t) => t.id !== teamId);
    setSavedTeams(updatedTeams);
    localStorage.setItem("savedTeams", JSON.stringify(updatedTeams));
  };

  const togglePosition = (position: string) => {
    setSelectedPositions((prev) => {
      const next = new Set(prev);
      if (next.has(position)) {
        next.delete(position);
      } else {
        next.add(position);
      }
      return next;
    });
  };

  const handleGetRecommendations = async () => {
    setRecommendationError("");

    if (!isRosterComplete) {
      const formatted = incompletePositions.join(", ");
      setRecommendationError(
        `Fill your lineup before requesting recommendations. Missing: ${formatted}`
      );
      return;
    }

    const playerIds = positionOrder
      .map((pos) => lineup[pos]?.id)
      .filter((id): id is number => typeof id === "number");

    if (playerIds.length === 0) {
      setRecommendationError("Select players to build your lineup first.");
      return;
    }

    setIsRecommending(true);
    setRecommendedPlayers([]);

    const result = await playerActions.getRecommendations(playerIds);

    setIsRecommending(false);

    if (result.success && result.data) {
      if (result.data.length === 0) {
        setRecommendationError("No recommendations available. Try adjusting your lineup.");
        return;
      }
      setRecommendedPlayers(result.data);
      return;
    }

    setRecommendationError(result.error || "Failed to fetch recommendations.");
  };

  const toggleAllPositions = () => {
    if (selectedPositions.size === positionOrder.length) {
      setSelectedPositions(new Set());
    } else {
      setSelectedPositions(new Set(positionOrder));
    }
  };


  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.kicker}>Team Builder</div>
      </header>

      <div className={styles.builderShell}>
        {/* LEFT COLUMN */}
        <div className={styles.leftColumn}>
          {/* Search section with Load a team and Filters */}
          <section className={styles.searchSection}>
            <div className={styles.searchBar}>
              <span className={styles.searchIcon}>🔍</span>
              <input
                type="text"
                placeholder="Search players by name, team, or position…"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const first =
                      availablePlayers.find((p) => !assignedIds.has(p.id)) ||
                      availablePlayers[0];
                    if (first && activePosition) assignPlayerToPosition(first, activePosition);
                  }
                }}
              />
            </div>

            <div className={styles.searchStatus}>
              {searchTerm.trim() ? `${availablePlayers.length} results` : `${savedPlayers.length} saved players`}
            </div>

            <div className={styles.searchActions}>
              <button 
                className={styles.loadTeamBtn}
                onClick={() => setLoadTeamOpen(!loadTeamOpen)}
              >
                Load a team {loadTeamOpen ? "▲" : "▼"}
              </button>
              <button 
                className={styles.filtersBtn}
                onClick={() => setFiltersOpen(!filtersOpen)}
              >
                Filters {filtersOpen ? "▲" : "▼"}
              </button>
            </div>

            {/* Load team panel */}
            {loadTeamOpen && (
              <div className={styles.loadTeamPanel}>
                {savedTeams.length === 0 ? (
                  <div className={styles.emptyTeams}>
                    <span>No saved teams yet. Save your current lineup to get started!</span>
                  </div>
                ) : (
                  <div className={styles.teamsList}>
                    {savedTeams.map((team) => (
                      <div key={team.id} className={styles.teamItem}>
                        <div className={styles.teamItemInfo}>
                          <strong>{team.name}</strong>
                          <span className={styles.teamDate}>
                            {new Date(team.savedAt).toLocaleDateString()}
                          </span>
                        </div>
                        <div className={styles.teamItemActions}>
                          <button
                            className={styles.loadBtn}
                            onClick={() => loadTeam(team)}
                          >
                            Load
                          </button>
                          <button
                            className={styles.deleteBtn}
                            onClick={() => deleteTeam(team.id)}
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Filters panel */}
            {filtersOpen && (
              <div className={styles.filtersPanel}>
                <div className={styles.filterSection}>
                  <label className={styles.filterLabel}>Salary Range</label>
                  <div className={styles.salaryInputs}>
                    <input
                      type="number"
                      className={styles.salaryInput}
                      placeholder="Min"
                      value={salaryRange[0]}
                      onChange={(e) => setSalaryRange([Number(e.target.value), salaryRange[1]])}
                      min={0}
                      max={salaryRange[1]}
                    />
                    <span className={styles.salaryDivider}>to</span>
                    <input
                      type="number"
                      className={styles.salaryInput}
                      placeholder="Max"
                      value={salaryRange[1]}
                      onChange={(e) => setSalaryRange([salaryRange[0], Number(e.target.value)])}
                      min={salaryRange[0]}
                      max={100000000}
                    />
                  </div>
                          
                  {/* Dual range sliders */}
                  <div style={{ position: 'relative', height: '6px', marginTop: '8px' }}>
                    <input
                      type="range"
                      className={styles.salarySlider}
                      min={0}
                      max={100000000}
                      step={1000000}
                      value={salaryRange[0]}
                      onChange={(e) => setSalaryRange([Math.min(Number(e.target.value), salaryRange[1] - 1000000), salaryRange[1]])}
                      style={{ position: 'absolute', width: '100%', pointerEvents: 'auto' }}
                    />
                    <input
                      type="range"
                      className={styles.salarySlider}
                      min={0}
                      max={100000000}
                      step={1000000}
                      value={salaryRange[1]}
                      onChange={(e) => setSalaryRange([salaryRange[0], Math.max(Number(e.target.value), salaryRange[0] + 1000000)])}
                      style={{ position: 'absolute', width: '100%', pointerEvents: 'auto' }}
                    />
                  </div>
                  
                  <div className={styles.salaryLabels}>
                    <span>${(salaryRange[0] / 1000000).toFixed(0)}M</span>
                    <span>${(salaryRange[1] / 1000000).toFixed(0)}M</span>
                  </div>
                </div>

                <div className={styles.filterSection}>
                  <div className={styles.positionHeader}>
                    <label className={styles.filterLabel}>Current Position</label>
                    <button 
                      className={styles.selectAllBtn}
                      onClick={toggleAllPositions}
                    >
                      {selectedPositions.size === positionOrder.length ? "Deselect All" : "Select All"}
                    </button>
                  </div>
                  <div className={styles.positionGrid}>
                    {positionOrder.map((pos) => (
                      <label key={pos} className={styles.positionCheckbox}>
                        <input
                          type="checkbox"
                          checked={selectedPositions.has(pos)}
                          onChange={() => togglePosition(pos)}
                        />
                        <span>{pos}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
          
          {/* Display box: player results */}
          <div className={styles.displayBox}>
            <div className={styles.playerScroller}>
              {availablePlayers.length === 0 && (
                <div className={styles.emptyState}>
                  <strong>No players found</strong>
                  <span>Try a different search or save some players.</span>
                </div>
              )}

              {availablePlayers.map((player) => {
                const alreadyAssigned = assignedIds.has(player.id);
                return (
                  <div
                    key={player.id}
                    className={`${styles.playerRow} ${draggingId === player.id ? styles.dragging : ""}`}
                    draggable={!alreadyAssigned}
                    onDragStart={() => !alreadyAssigned && prepareDragPlayer(player)}
                    onDragEnd={clearDragState}
                  >
                    <div className={styles.playerProfile}>
                      <img
                        src={player.image_url || DEFAULT_PLAYER_IMAGE}
                        alt={player.name}
                      />
                      <div>
                        <p className={styles.playerName}>{player.name}</p>
                        <div className={styles.playerMeta}>
                          {player.years_active || "N/A"}
                        </div>
                      </div>
                    </div>

                    <button
                      className={styles.addButton}
                      disabled={alreadyAssigned || !activePosition}
                      onClick={() => {
                        if (activePosition) assignPlayerToPosition(player, activePosition);
                      }}
                      title={
                        alreadyAssigned
                          ? "Already assigned"
                          : !activePosition
                          ? "Select a position first"
                          : "Add to active position"
                      }
                    >
                      {alreadyAssigned ? "Assigned" : "Add"}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
          {/* BOTTOM-RIGHT: Target Metrics + Get Recommendations */}
        <section className={styles.actionsCard}>
          {/* <button className={styles.targetMetricsBtn}>Team Target Metrics ▼</button> */}
          <div className={styles.recommendRow}>
            <span className={styles.recommendCopy}>Click to get recommendations</span>
            <button
              className={styles.recommendBtn}
              onClick={handleGetRecommendations}
              disabled={isRecommending || !isRosterComplete}
            >
              {isRecommending ? "Loading..." : "Get Recommendations!"}
            </button>
          </div>
          {!isRosterComplete && (
            <div className={styles.recommendHint}>
              Select players for every position before requesting recommendations.
            </div>
          )}
          {recommendationError && (
            <div className={styles.recommendError}>{recommendationError}</div>
          )}
          {isRecommending && !recommendationError && (
            <div className={styles.recommendLoading}>Calculating best fits…</div>
          )}
          {recommendedPlayers.length > 0 && (
            <ul className={styles.recommendList}>
              {recommendedPlayers.map((player) => (
                <li key={player.id} className={styles.recommendItem}>
                  <div className={styles.recommendPlayerInfo}>
                    <img
                      src={player.image_url || DEFAULT_PLAYER_IMAGE}
                      alt={player.name}
                    />
                    <div>
                      <div className={styles.recommendName}>{player.name}</div>
                      <div className={styles.recommendMeta}>{player.years_active}</div>
                    </div>
                  </div>
                  <span className={styles.recommendScore}>
                    Impact Score: {player.score.toFixed(1)}
                  </span>
                </li>
              ))}
            </ul>
          )}
          
        </section>
        </div>

        {/* TOP-RIGHT: Team card */}
        <section className={styles.teamCard}>
          <div className={styles.teamInfo}>
            <div className={styles.teamNameWrapper}>
              {isEditingTeamName ? (
                <input
                  type="text"
                  className={styles.teamNameInput}
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  onBlur={() => setIsEditingTeamName(false)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") setIsEditingTeamName(false);
                  }}
                  autoFocus
                />
              ) : (
                <h2 className={styles.teamName}>
                  {teamName}
                  <span
                    className={styles.editIcon}
                    onClick={() => setIsEditingTeamName(true)}
                  >
                    ✏️
                  </span>
                </h2>
              )}
            </div>

            <div className={styles.teamScore}>
              <label>Team Score</label>
              <span>123456</span>
            </div>
            <div className={styles.teamBudget}>
              <label>Team Budget</label>
              <span>$255,380,936</span>
            </div>
            <div className={styles.otherStat}>
              <label>someOtherStat</label>
              <span>255,380,936</span>
            </div>
          </div>
          <div className={styles.radarChart}>Radar Chart</div>
        </section>

        {/* MIDDLE-RIGHT: Diamond */}
        <section className={styles.diamondPanel}>
          <div className={styles.panelHeader}>
            <div>
              <h2>Your lineup</h2>
              <p>Select a position, then add or drag a player.</p>
            </div>
            <span className={styles.positionHint}>
              {activePosition ? `Active: ${activePosition}` : "Pick a position"}
            </span>
          </div>

          <div className={styles.diamond}>
            <svg className={styles.diamondLines} viewBox="0 0 100 100" preserveAspectRatio="none">
              <rect x="5" y="5" width="90" height="90" rx="8" ry="8" />
              <line x1="50" y1="10" x2="10" y2="50" />
              <line x1="50" y1="10" x2="90" y2="50" />
              <line x1="10" y1="50" x2="50" y2="90" />
              <line x1="50" y1="90" x2="90" y2="50" />
              <circle cx="50" cy="12" r="2" />
              <circle cx="50" cy="50" r="2" />
            </svg>

            {positionOrder.map((pos) => {
              const assigned = lineup[pos];
              const isActive = activePosition === pos;
              const canDrop = dragPlayerRef.current && !assigned;
              return (
                <div
                  key={pos}
                  className={`${styles.positionNode} ${assigned ? styles.filled : ""} ${
                    isActive ? styles.active : ""
                  } ${canDrop && dropTarget === pos ? styles.droppable : ""}`}
                  style={positionCoordinates[pos]}
                >
                  <button
                    type="button"
                    className={styles.positionTrigger}
                    onClick={() => setActivePosition(pos)}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setDropTarget(pos);
                    }}
                    onDragLeave={() => setDropTarget(null)}
                    onDrop={(e) => handlePositionDrop(e, pos)}
                    draggable={!!assigned}
                    onDragStart={() => assigned && prepareDragPlayer(assigned, pos)}
                    onDragEnd={clearDragState}
                    aria-label={`Position ${pos}`}
                  >
                    {assigned ? (
                      <div className={styles.positionPlayer}>
                        <img src={assigned.image_url || DEFAULT_PLAYER_IMAGE} alt={assigned.name} />
                        <div className={styles.positionName}>{assigned.name}</div>
                      </div>
                    ) : (
                      <>
                        <div className={styles.positionLabel}>{pos}</div>
                        <div style={{ fontSize: 12, opacity: 0.7 }}>Drop or click</div>
                      </>
                    )}
                  </button>

                  {assigned && (
                    <button
                      className={styles.clearSlot}
                      onClick={() => handleClearSlot(pos)}
                      title="Clear"
                    >
                      ×
                    </button>
                  )}
                </div>
              );
            })}

            {staticSpots.map((spot) => (
              <div
                key={spot.label}
                className={`${styles.positionNode} ${styles.staticPosition}`}
                style={{ top: spot.top, left: spot.left }}
                aria-hidden="true"
              >
                <div className={styles.positionLabel}>{spot.label}</div>
                <div className={styles.staticHint}>Pitcher</div>
              </div>
            ))}
          </div>

          <button 
            className={styles.addButton} 
            style={{ alignSelf: "flex-end", marginTop: 12 }}
            onClick={saveTeam}
          >
            Save Lineup
          </button>
        </section>

      </div>
    </div>
  );
}