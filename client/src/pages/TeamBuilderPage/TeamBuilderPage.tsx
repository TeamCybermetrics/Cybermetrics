import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent } from "react";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer, TeamWeaknessResponse, PlayerValueScore } from "@/api/players";
import { PageCard, Card } from "@/components";
import styles from "./TeamBuilderPage.module.css";
import {
  DiamondPosition,
  LineupState,
  SavedTeam,
  positionOrder,
} from "@/components/TeamBuilder/constants";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SavedPlayersSection } from "@/components/TeamBuilder/SavedPlayersSection/SavedPlayersSection";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { DiamondPanel } from "@/components/TeamBuilder/DiamondPanel/DiamondPanel";
import { TeamPerformanceCard } from "@/components/TeamBuilder/TeamPerformanceCard/TeamPerformanceCard";

/**
 * Interactive team builder page that lets users search and manage players, construct a lineup using click or drag-and-drop, apply filters, and save or load teams to localStorage.
 *
 * @returns The React element rendering the Team Builder page.
 */
export default function TeamBuilderPage() {
  const [lineup, setLineup] = useState<LineupState>(() =>
    positionOrder.reduce((acc, position) => ({ ...acc, [position]: null }), {} as LineupState)
  );
  const lineupRef = useRef(lineup);
  const [activePosition, setActivePosition] = useState<DiamondPosition | null>("CF");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [savedPlayersLoaded, setSavedPlayersLoaded] = useState(false);
  const searchControllerRef = useRef<AbortController | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [teamName] = useState("TeamName1");
  const [savedTeams, setSavedTeams] = useState<SavedTeam[]>([]);

  const [savingPlayerIds, setSavingPlayerIds] = useState<Set<number>>(() => new Set());
  const [deletingPlayerIds, setDeletingPlayerIds] = useState<Set<number>>(() => new Set());
  const [playerOperationError, setPlayerOperationError] = useState("");

  // Team analysis state
  const [teamWeakness, setTeamWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [playerScores, setPlayerScores] = useState<PlayerValueScore[]>([]);
  const [benchReplacements, setBenchReplacements] = useState<Map<number, { replacesPosition: string; replacesName: string; delta: number }>>(new Map());
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const analysisRequestId = useRef(0);

  useEffect(() => {
    lineupRef.current = lineup;
  }, [lineup]);

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
      try {
      const result = await playerActions.getSavedPlayers();
      if (result.success && result.data) {
        setSavedPlayers(result.data);
        } else if (!result.success) {
          setPlayerOperationError(result.error || "Failed to load saved players");
        }
      } finally {
        setSavedPlayersLoaded(true);
      }
    };

    void fetchSaved();
  }, []);

  // Get player IDs from lineup (only players with positions)
  const lineupPlayerIds = useMemo(
    () =>
      Object.values(lineup)
        .filter((player): player is SavedPlayer => player !== null)
        .map((player) => player.id),
    [lineup]
  );

  // Get all saved player IDs for scoring
  const allSavedPlayerIds = useMemo(
    () => savedPlayers.map((player) => player.id),
    [savedPlayers]
  );

  // Load team analysis when lineup or saved players change
  useEffect(() => {
    const loadAnalysis = async () => {
      const requestId = ++analysisRequestId.current;
      
      if (allSavedPlayerIds.length === 0) {
        setTeamWeakness(null);
        setPlayerScores([]);
        return;
      }

      setLoadingAnalysis(true);

      try {
        // Calculate weakness based on lineup (9 players)
        // Calculate scores ONLY for lineup players (their contribution to the 9-player team)
        // For bench players, we calculate based on full roster (approximation of replacement value)
        const [weaknessRes, lineupScoresRes, benchScoresRes] = await Promise.all([
          lineupPlayerIds.length > 0 
            ? playerActions.getTeamWeakness(lineupPlayerIds)
            : Promise.resolve({ success: true, data: null }),
          lineupPlayerIds.length > 0
            ? playerActions.getPlayerValueScores(lineupPlayerIds)
            : Promise.resolve({ success: true, data: [] }),
          allSavedPlayerIds.length > 0
            ? playerActions.getPlayerValueScores(allSavedPlayerIds)
            : Promise.resolve({ success: true, data: [] })
        ]);

        if (analysisRequestId.current !== requestId) {
          return;
        }

        if (weaknessRes.success && weaknessRes.data) {
          setTeamWeakness(weaknessRes.data);
        } else {
          setTeamWeakness(null);
        }

        // Process scores
        const lineupScores = lineupScoresRes.success ? (lineupScoresRes.data || []) : [];
        const allScores = benchScoresRes.success ? (benchScoresRes.data || []) : [];
        
        // Create a map of lineup player IDs for quick lookup
        const lineupPlayerIdSet = new Set(lineupPlayerIds);
        
        // Create score map for easy lookup
        const scoreMap = new Map(allScores.map(s => [s.id, s]));
        
        // Get bench players
        const benchPlayers = savedPlayers.filter(p => !lineupPlayerIdSet.has(p.id));
        
        // Calculate replacement values for bench players based on active position
        const replacementMap = new Map<number, { replacesPosition: string; replacesName: string; delta: number }>();
        
        // Only calculate if there's an active position selected
        if (activePosition) {
          const activePositionPlayer = lineup[activePosition];
          
          if (activePositionPlayer) {
            const activePositionScore = scoreMap.get(activePositionPlayer.id);
            
            if (activePositionScore) {
              // Calculate current team total score
              const currentTeamScore = lineupScores.reduce((sum, score) => sum + score.adjustment_score, 0);
              
              // For each bench player, calculate the new team score if they replace the active position
              for (const benchPlayer of benchPlayers) {
                const benchScore = scoreMap.get(benchPlayer.id);
                if (!benchScore) continue;
                
                // New team score = current team score - removed player + added player
                const newTeamScore = currentTeamScore - activePositionScore.adjustment_score + benchScore.adjustment_score;
                const delta = newTeamScore - currentTeamScore;
                
                replacementMap.set(benchPlayer.id, {
                  replacesPosition: activePosition,
                  replacesName: activePositionPlayer.name,
                  delta: delta
                });
              }
            }
          }
        }
        
        setBenchReplacements(replacementMap);
        
        // For playing players, use their lineup contribution scores
        // For bench players, show their score relative to who they'd replace
        const combinedScores = [
          ...lineupScores,
          ...benchPlayers.map(p => {
            const score = scoreMap.get(p.id);
            const replacement = replacementMap.get(p.id);
            if (score && replacement) {
              // Show the delta (improvement) as the score for bench players
              return {
                ...score,
                adjustment_score: replacement.delta
              };
            }
            return score;
          }).filter((s): s is PlayerValueScore => s !== undefined)
        ];
        
        setPlayerScores(combinedScores);
      } catch (error) {
        if (analysisRequestId.current !== requestId) {
          return;
        }
        setTeamWeakness(null);
        setPlayerScores([]);
      } finally {
        if (analysisRequestId.current === requestId) {
          setLoadingAnalysis(false);
        }
      }
    };

    // Debounce analysis updates
    const timer = setTimeout(() => {
      void loadAnalysis();
    }, 500);

    return () => clearTimeout(timer);
  }, [lineupPlayerIds, allSavedPlayerIds, activePosition]);

  const ensurePlayerIsSaved = useCallback(
    async (player: SavedPlayer) => {
      if (savedPlayers.some((saved) => saved.id === player.id)) {
        return true;
      }

      const result = await playerActions.addPlayer({
        id: player.id,
        name: player.name,
        image_url: player.image_url,
        years_active: player.years_active
      });

      if (result.success) {
        setSavedPlayers((prev) => [...prev, player]);
        return true;
      }

      setPlayerOperationError(result.error || "Failed to save player");
      return false;
    },
    [savedPlayers]
  );

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

  const buildLineupFromSavedPlayers = useCallback((players: SavedPlayer[]) => {
    return positionOrder.reduce((acc, position) => {
      const playerForSlot = players.find((saved) => saved.position === position) || null;
      acc[position] = playerForSlot;
      return acc;
    }, {} as LineupState);
  }, []);

  useEffect(() => {
    if (!savedPlayersLoaded) {
      return;
    }

    const nextLineup = buildLineupFromSavedPlayers(savedPlayers);
    setLineup((prev) => {
      const hasChanges = positionOrder.some(
        (position) => (prev[position]?.id ?? null) !== (nextLineup[position]?.id ?? null)
      );
      return hasChanges ? nextLineup : prev;
    });
  }, [savedPlayers, savedPlayersLoaded, buildLineupFromSavedPlayers]);

  const trimmedSearchTerm = searchTerm.trim();
  const hasSearchTerm = trimmedSearchTerm.length > 0;

  const handleSearchTermChange = useCallback((value: string) => {
    setSearchTerm(value);
    if (value.trim()) {
      setSearchModalOpen(true);
    }
  }, []);

  const handleSearchBarFocus = useCallback(() => {
    setSearchModalOpen(true);
  }, []);

  const handleCloseSearchModal = useCallback(() => {
    setSearchModalOpen(false);
    setSearchTerm("");
    setSearchResults([]);
  }, []);

  const searchResultPlayers = useMemo(() => {
    if (!hasSearchTerm) {
      return [];
    }
      return searchResults.map((result) => ({
        id: result.id,
        name: result.name,
        image_url: result.image_url,
        years_active: result.years_active
      })) as SavedPlayer[];
  }, [hasSearchTerm, searchResults]);

  const savedPlayerIds = useMemo(
    () =>
      new Set(
        savedPlayers
          .map((player) => player.id)
          .filter((id): id is number => typeof id === "number")
      ),
    [savedPlayers]
  );

  useEffect(() => {
    if (!searchModalOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        handleCloseSearchModal();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [searchModalOpen, handleCloseSearchModal]);

  const persistPlayerPosition = useCallback(
    async (playerId: number, position: DiamondPosition | null) => {
      const result = await playerActions.updatePlayerPosition(playerId, position);
      if (result.success && result.data) {
        setPlayerOperationError("");
        setSavedPlayers((prev) => {
          const index = prev.findIndex((saved) => saved.id === playerId);
          if (index === -1) {
            return [...prev, result.data];
          }
          return prev.map((saved, idx) =>
            idx === index ? { ...saved, ...result.data } : saved
          );
        });
      } else if (!result.success) {
        setPlayerOperationError(result.error || "Failed to update player position");
      }
    },
    []
  );

  const assignPlayerToPosition = useCallback(
    (player: SavedPlayer, position: DiamondPosition) => {
      const currentLineup = lineupRef.current;
      const replacedPlayer = currentLineup[position];

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

      setSavedPlayers((prev) => {
        const updated = prev.map((saved) => {
          if (saved.id === player.id) {
            return { ...saved, position };
          }
          if (replacedPlayer && saved.id === replacedPlayer.id && replacedPlayer.id !== player.id) {
            return { ...saved, position: null };
          }
          return saved;
        });

        if (!prev.some((saved) => saved.id === player.id)) {
          updated.push({ ...player, position });
        }

        if (
          replacedPlayer &&
          replacedPlayer.id !== player.id &&
          !prev.some((saved) => saved.id === replacedPlayer.id)
        ) {
          updated.push({ ...replacedPlayer, position: null });
        }

        return updated;
      });

      void persistPlayerPosition(player.id, position);
      if (replacedPlayer && replacedPlayer.id !== player.id) {
        void persistPlayerPosition(replacedPlayer.id, null);
      }
    },
    [persistPlayerPosition]
  );

  const handleAddPlayer = useCallback(
    async (player: SavedPlayer) => {
      if (!activePosition) {
        return;
      }

      setPlayerOperationError("");
      setSavingPlayerIds((prev) => {
        const next = new Set(prev);
        next.add(player.id);
        return next;
      });

      try {
        const saved = await ensurePlayerIsSaved(player);
        if (saved) {
          assignPlayerToPosition(player, activePosition);
        }
      } finally {
        setSavingPlayerIds((prev) => {
          const next = new Set(prev);
          next.delete(player.id);
          return next;
        });
      }
    },
    [activePosition, assignPlayerToPosition, ensurePlayerIsSaved]
  );

  const handleDeletePlayer = useCallback(
    async (player: SavedPlayer) => {
      setPlayerOperationError("");
      setDeletingPlayerIds((prev) => {
        const next = new Set(prev);
        next.add(player.id);
        return next;
      });

      try {
        const result = await playerActions.deletePlayer(player.id);
        if (!result.success) {
          setPlayerOperationError(result.error || "Failed to delete player");
          return;
        }

        setSavedPlayers((prev) => prev.filter((saved) => saved.id !== player.id));
        setLineup((prev) => {
          let updated = false;
          const next: LineupState = { ...prev };
          positionOrder.forEach((pos) => {
            if (next[pos]?.id === player.id) {
              next[pos] = null;
              updated = true;
            }
          });
          return updated ? next : prev;
        });
      } finally {
        setDeletingPlayerIds((prev) => {
          const next = new Set(prev);
          next.delete(player.id);
          return next;
        });
      }
    },
    []
  );

  const handleClearSlot = (position: DiamondPosition) => {
    const player = lineupRef.current[position];
    if (!player) {
      return;
    }

    setLineup((prev) => ({
      ...prev,
      [position]: null
    }));

    setSavedPlayers((prev) => {
      const found = prev.some((saved) => saved.id === player.id);
      if (!found) {
        return [...prev, { ...player, position: null }];
      }
      return prev.map((saved) =>
        saved.id === player.id ? { ...saved, position: null } : saved
      );
    });

    void persistPlayerPosition(player.id, null);
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

  const handlePositionDrop = async (event: DragEvent<HTMLButtonElement>, position: DiamondPosition) => {
    event.preventDefault();
    event.stopPropagation();
    const player = dragPlayerRef.current;
    if (!player) {
      clearDragState();
      return;
    }

    try {
      setPlayerOperationError("");
      const saved = await ensurePlayerIsSaved(player);
      if (saved) {
    assignPlayerToPosition(player, position);
      }
    } finally {
    clearDragState();
    }
  };

  const saveTeam = () => {
    const newTeam: SavedTeam = {
      id: Date.now().toString(),
      name: teamName,
      lineup: lineup, // The 9 active players in positions
      fullRoster: savedPlayers, // All saved players (including bench)
      savedAt: new Date().toISOString()
    };

    const updatedTeams = [...savedTeams, newTeam];
    setSavedTeams(updatedTeams);
    localStorage.setItem("savedTeams", JSON.stringify(updatedTeams));
    alert(`Team "${teamName}" saved successfully!`);
  };

  const handleSavePlayerOnly = useCallback(
    async (player: SavedPlayer) => {
      setPlayerOperationError("");
      setSavingPlayerIds((prev) => {
      const next = new Set(prev);
        next.add(player.id);
        return next;
      });

      try {
        const saved = await ensurePlayerIsSaved(player);
        if (saved) {
          setSavedPlayers((prev) => {
            if (prev.some((existing) => existing.id === player.id)) {
              return prev;
            }
            return [...prev, player];
          });
        }
      } finally {
        setSavingPlayerIds((prev) => {
          const next = new Set(prev);
          next.delete(player.id);
      return next;
    });
      }
    },
    [ensurePlayerIsSaved]
  );

  return (
    <PageCard title="Lineup Constructor">
      <div className={styles.builderShell}>
        {/* LEFT COLUMN */}
        <div className={styles.leftColumn}>
          {/* Search section with Load a team and Filters */}
          <Card title="Search Players">
            <SearchBar
              searchTerm={searchTerm}
              onSearchTermChange={handleSearchTermChange}
              statusText={
                hasSearchTerm
                  ? `${searchResultPlayers.length} results`
                  : `${savedPlayers.length} saved players`
              }
              errorMessage={playerOperationError}
              onFocus={handleSearchBarFocus}
            />
          </Card>

          {hasSearchTerm && (
            <SearchResultsSection
              players={searchResultPlayers}
              savedPlayerIds={savedPlayerIds}
              assignedIds={assignedIds}
              draggingId={draggingId}
              savingPlayerIds={savingPlayerIds}
              onPrepareDrag={prepareDragPlayer}
              onClearDrag={clearDragState}
              onSavePlayer={(player) => void handleSavePlayerOnly(player)}
            />
          )}

          <SavedPlayersSection
            players={savedPlayers}
            assignedIds={assignedIds}
            draggingId={draggingId}
            deletingPlayerIds={deletingPlayerIds}
            onPrepareDrag={prepareDragPlayer}
            onClearDrag={clearDragState}
            onDeletePlayer={handleDeletePlayer}
            playerScores={playerScores}
            benchReplacements={benchReplacements}
          />
        </div>

        <DiamondPanel
          lineup={lineup}
          activePosition={activePosition}
          dropTarget={dropTarget}
          dragPlayer={dragPlayerRef.current}
          onSelectPosition={(position) => setActivePosition(position)}
          onDragOverPosition={(position) => setDropTarget(position)}
          onDragLeavePosition={() => setDropTarget(null)}
          onDropOnPosition={handlePositionDrop}
          onPrepareDrag={prepareDragPlayer}
          onClearDragState={clearDragState}
          onClearSlot={handleClearSlot}
          onSaveTeam={saveTeam}
        />

        <TeamPerformanceCard
          weakness={teamWeakness}
          loading={loadingAnalysis}
          hasLineup={lineupPlayerIds.length > 0}
        />

      </div>

      {searchModalOpen && (
        <div className={styles.searchModalBackdrop} onClick={handleCloseSearchModal}>
          <div className={styles.searchModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.searchModalHeader}>
              <div>
                <p className={styles.searchModalKicker}>Search Players</p>
                <h3 className={styles.searchModalTitle}>Add Players to Your Lineup</h3>
              </div>
              <button className={styles.searchModalClose} onClick={handleCloseSearchModal}>
                ✕
              </button>
            </div>

            <div className={styles.searchModalInput}>
              <SearchBar
                searchTerm={searchTerm}
                onSearchTermChange={handleSearchTermChange}
                statusText={
                  hasSearchTerm
                    ? `${searchResultPlayers.length} results`
                    : "Type a player name to begin searching"
                }
                errorMessage={playerOperationError}
                autoFocus
              />
            </div>

            <div className={styles.searchModalResults}>
              {hasSearchTerm ? (
                <SearchResultsSection
                  players={searchResultPlayers}
                  savedPlayerIds={savedPlayerIds}
                  assignedIds={assignedIds}
                  draggingId={draggingId}
                  savingPlayerIds={savingPlayerIds}
                  onPrepareDrag={prepareDragPlayer}
                  onClearDrag={clearDragState}
                  onSavePlayer={(player) => void handleSavePlayerOnly(player)}
                />
              ) : (
                <div className={styles.searchModalEmpty}>Start typing to see the results</div>
              )}
            </div>
          </div>
        </div>
      )}
    </PageCard>
  );
}
