import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent } from "react";
import { playerActions } from "@/actions/players";
import type { SavedPlayer, TeamWeaknessResponse } from "@/api/players";
import { LineupState, positionOrder, type DiamondPosition } from "@/components/TeamBuilder/constants";

export type PanelMode = "idle" | "recommendations" | "search";

export function useRecommendations() {
  // Lineups
  const initialLineup: LineupState = useMemo(
    () => positionOrder.reduce((acc, position) => ({ ...acc, [position]: null }), {} as LineupState),
    []
  );
  const [lineup, setLineup] = useState<LineupState>(initialLineup);
  const [baselineLineup, setBaselineLineup] = useState<LineupState>(initialLineup);

  // Weakness data
  const [baselineWeakness, setBaselineWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [currentWeakness, setCurrentWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [weaknessLoading, setWeaknessLoading] = useState(false);
  const [weaknessError, setWeaknessError] = useState<string | null>(null);

  const [mode, setMode] = useState<PanelMode>("idle");

  // Search
  const [searchResults, setSearchResults] = useState<SavedPlayer[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Recommendations
  const [recommendedPlayers, setRecommendedPlayers] = useState<SavedPlayer[]>([]);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);

  const [activePosition, setActivePosition] = useState<DiamondPosition>("CF");
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);

  // Saved players
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [playerOperationError, setPlayerOperationError] = useState<string | null>(null);
  const [savingLineup, setSavingLineup] = useState(false);

  const buildLineupFromSaved = useCallback((players: SavedPlayer[]) => {
    const next: LineupState = positionOrder.reduce(
      (acc, pos) => ({ ...acc, [pos]: null }),
      {} as LineupState
    );
    players.forEach((p) => {
      if (p.position && positionOrder.includes(p.position as DiamondPosition)) {
        next[p.position as DiamondPosition] = p;
      }
    });
    return next;
  }, []);

  const onSearchChange = (value: string) => {
    setQuery(value);
    setMode(value ? "search" : "idle");
  };

  const getPlayerIdsFromLineup = useCallback((state: LineupState) => {
    return positionOrder
      .map((pos) => state[pos]?.id)
      .filter((id): id is number => typeof id === "number");
  }, []);

  const fetchWeaknessFor = useCallback(async (state: LineupState) => {
    const ids = getPlayerIdsFromLineup(state);
    if (ids.length === 0) return null;
    const result = await playerActions.getTeamWeakness(ids);
    if (result.success && result.data) return result.data;
    throw new Error(result.error || "Failed to load team weaknesses");
  }, [getPlayerIdsFromLineup]);

  const refreshWeakness = useCallback(
    async (workingOverride?: LineupState, baselineOverride?: LineupState) => {
      const working = workingOverride ?? lineup;
      const baseline = baselineOverride ?? baselineLineup;
      const hasAnyPlayers =
        getPlayerIdsFromLineup(working).length > 0 || getPlayerIdsFromLineup(baseline).length > 0;
    if (!hasAnyPlayers) {
      setBaselineWeakness(null);
      setCurrentWeakness(null);
      return;
    }
    setWeaknessLoading(true);
    setWeaknessError(null);
    try {
      const [base, current] = await Promise.all([
        fetchWeaknessFor(baseline),
        fetchWeaknessFor(working),
      ]);
      setBaselineWeakness(base);
      setCurrentWeakness(current);
    } catch (e) {
      setWeaknessError(e instanceof Error ? e.message : "Failed to load weaknesses");
    } finally {
      setWeaknessLoading(false);
    }
    },
    [baselineLineup, lineup, fetchWeaknessFor, getPlayerIdsFromLineup]
  );

  // Keep weakness in sync with working/baseline lineups
  useEffect(() => {
    void refreshWeakness();
  }, [refreshWeakness]);

  // Load saved players once
  useEffect(() => {
    const loadSaved = async () => {
      const result = await playerActions.getSavedPlayers();
      if (result.success && result.data) {
        setSavedPlayers(result.data);
        const nextLineup = buildLineupFromSaved(result.data);
        setLineup(nextLineup);
        setBaselineLineup(nextLineup);
      } else if (!result.success) {
        setPlayerOperationError(result.error || "Failed to load saved players");
      }
    };
    void loadSaved();
  }, [buildLineupFromSaved]);

  // Search pipeline with debounce
  useEffect(() => {
    if (!query.trim()) {
      setSearchResults([]);
      setSearchError(null);
      setSearchLoading(false);
      setMode("idle");
      return;
    }
    setSearchLoading(true);
    setSearchError(null);
    const timer = setTimeout(async () => {
      const result = await playerActions.searchPlayers(query.trim());
      setSearchLoading(false);
      if (result.success && result.data) {
        const mapped: SavedPlayer[] = result.data.map((p) => ({
          id: p.id,
          name: p.name,
          image_url: p.image_url,
          years_active: p.years_active
        }));
        setSearchResults(mapped);
        setMode("search");
      } else if (result.aborted) {
        // do nothing
      } else {
        setSearchResults([]);
        setSearchError(result.error || "Search failed");
        setMode("idle");
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  const ensurePlayerSaved = useCallback(
    async (player: SavedPlayer) => {
      if (savedPlayers.some((p) => p.id === player.id)) return true;
      const result = await playerActions.addPlayer({
        id: player.id,
        name: player.name,
        image_url: player.image_url,
        years_active: player.years_active,
      });
      if (result.success) {
        setSavedPlayers((prev) => (prev.some((p) => p.id === player.id) ? prev : [...prev, player]));
        return true;
      }
      setPlayerOperationError(result.error || "Failed to save player");
      return false;
    },
    [savedPlayers]
  );

  const assignPlayerToLineup = useCallback(
    (player: SavedPlayer, position?: DiamondPosition) => {
      const target = position ?? activePosition;
      setLineup((prev) => {
        const next: LineupState = { ...prev };
        positionOrder.forEach((pos) => {
          if (next[pos]?.id === player.id) {
            next[pos] = null;
          }
        });
        next[target] = player;
        void refreshWeakness(next, baselineLineup);
        return next;
      });
      setActivePosition(target);
    },
    [activePosition, baselineLineup, refreshWeakness]
  );

  const handleAddFromSearch = useCallback(
    (player: SavedPlayer) => {
      void (async () => {
        const ok = await ensurePlayerSaved(player);
        if (ok) {
          assignPlayerToLineup(player);
          setMode("idle");
          setQuery("");
        }
      })();
    },
    [assignPlayerToLineup, ensurePlayerSaved]
  );

  const handleAddFromRecommendation = useCallback(
    (player: SavedPlayer) => {
      void (async () => {
        const ok = await ensurePlayerSaved(player);
        if (ok) {
          assignPlayerToLineup(player);
          setMode("recommendations");
        }
      })();
    },
    [assignPlayerToLineup, ensurePlayerSaved]
  );

  const handleGetRecommendations = useCallback(async () => {
    setRecommendationError(null);
    const playerIds = getPlayerIdsFromLineup(lineup);
    if (playerIds.length === 0) {
      setRecommendationError("Select players to build your lineup first.");
      setRecommendedPlayers([]);
      setMode("idle");
      return;
    }
    setRecommendationLoading(true);
    const result = await playerActions.getRecommendations(playerIds);
    setRecommendationLoading(false);
    if (result.success && result.data) {
      const mapped: SavedPlayer[] = result.data.map((p) => ({
        id: p.id,
        name: p.name,
        image_url: p.image_url,
        years_active: p.years_active
      }));
      setRecommendedPlayers(mapped);
      setMode("recommendations");
    } else {
      setRecommendedPlayers([]);
      setRecommendationError(result.error || "Failed to fetch recommendations");
      setMode("idle");
    }
  }, [getPlayerIdsFromLineup, lineup]);

  const handleClearSlot = useCallback(
    (position: DiamondPosition) => {
      setLineup((prev) => {
        const next = { ...prev, [position]: null };
        void refreshWeakness(next, baselineLineup);
        return next;
      });
    },
    [baselineLineup, refreshWeakness]
  );

  const prepareDragPlayer = useCallback((player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = player;
    setDraggingId(player.id);
    if (fromPosition) {
      setActivePosition(fromPosition);
    }
  }, []);

  const clearDragState = useCallback(() => {
    dragPlayerRef.current = null;
    setDraggingId(null);
    setDropTarget(null);
  }, []);

  const handlePositionDrop = useCallback(
    (e: DragEvent<HTMLButtonElement>, position: DiamondPosition) => {
      e.preventDefault();
      e.stopPropagation();
      const player = dragPlayerRef.current;
      if (!player) {
        clearDragState();
        return;
      }
      assignPlayerToLineup(player, position);
      clearDragState();
    },
    [assignPlayerToLineup, clearDragState]
  );

  const persistPositions = useCallback(async () => {
    const ops: Promise<unknown>[] = [];
    const assignedIds = new Set<number>();
    positionOrder.forEach((pos) => {
      const p = lineup[pos];
      if (p?.id) {
        assignedIds.add(p.id);
        const newPos = pos;
        const existing = savedPlayers.find((sp) => sp.id === p.id);
        if (!existing || existing.position !== newPos) {
          ops.push(playerActions.updatePlayerPosition(p.id, newPos));
        }
      }
    });
    // Clear positions for saved players not in lineup
    savedPlayers.forEach((sp) => {
      if (!sp.id) return;
      if (!assignedIds.has(sp.id) && sp.position) {
        ops.push(playerActions.updatePlayerPosition(sp.id, null));
      }
    });
    await Promise.all(ops);
    // update local savedPlayers positions to match lineup
    setSavedPlayers((prev) =>
      prev.map((sp) => {
        if (!sp.id) return sp;
        const pos = positionOrder.find((slot) => lineup[slot]?.id === sp.id) || null;
        return { ...sp, position: pos };
      })
    );
  }, [lineup, savedPlayers]);

  const onSaveLineup = useCallback(async () => {
    setSavingLineup(true);
    setPlayerOperationError(null);
    try {
      await persistPositions();
      setBaselineLineup(lineup);
      if (currentWeakness) {
        setBaselineWeakness(currentWeakness);
      }
    } catch (e) {
      setPlayerOperationError(e instanceof Error ? e.message : "Failed to save lineup");
    } finally {
      setSavingLineup(false);
    }
  }, [persistPositions, lineup, currentWeakness]);

  return {
    mode,
    query,
    lineup,
    baselineLineup,
    baselineWeakness,
    currentWeakness,
    weaknessLoading,
    weaknessError,
    searchResults,
    searchLoading,
    searchError,
    recommendedPlayers,
    recommendationLoading,
    recommendationError,
    activePosition,
    dropTarget,
    draggingId,
    setActivePosition,
    setDropTarget,
    setLineup,
    setBaselineLineup,
    savedPlayers,
    onGetRecommendations: handleGetRecommendations,
    onSearchChange,
    onAddFromSearch: handleAddFromSearch,
    onAddFromRecommendation: handleAddFromRecommendation,
    onClearSlot: handleClearSlot,
    onPrepareDrag: prepareDragPlayer,
    onClearDrag: clearDragState,
    onPositionDrop: handlePositionDrop,
    onSaveLineup,
    savingLineup,
    playerOperationError,
  };
}
