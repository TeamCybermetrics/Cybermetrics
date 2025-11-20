import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { playerActions } from "@/actions/players";
import type { SavedPlayer, TeamWeaknessResponse, PlayerValueScore } from "@/api/players";
import type { DiamondPosition } from "@/components/TeamBuilder/constants";

export type PanelMode = "idle" | "recommendations" | "search";

/**
 * Manages saved players, team weakness computation, search, recommendations, and drag state for the recommendations UI.
 *
 * Provides state and callbacks to load and update saved players, fetch team weakness for baseline and current saved rosters,
 * perform player search, request recommendations, manage concurrent save/delete operations, fetch player value scores,
 * and support dragging a player for position assignment.
 *
 * @returns An object exposing hook state and actions:
 * - mode: current panel mode ("idle" | "recommendations" | "search")
 * - searchTerm: current search input
 * - baselineWeakness, currentWeakness: computed weakness data for baseline and working teams (or `null`)
 * - weaknessLoading, weaknessError: loading flag and error message for weakness fetches
 * - activePosition, draggingId: current active diamond position and id of a dragging player (or `null`)
 * - searchResults, recommendedPlayers, savedPlayers: lists of players for search, recommendations, and saved team
 * - savedPlayerIds, assignedIds: Sets of saved player ids and ids with assigned positions
 * - savingPlayerIds, deletingPlayerIds: Sets tracking in-flight save/delete player operations
 * - playerScores: latest fetched player value scores
 * - hasSearchTerm, isRecommending, recommendationError, playerOperationError: derived flags and error strings
 * - setSearchTerm, setActivePosition: setters for search term and active position
 * - onPrepareDrag, onClearDrag: drag lifecycle callbacks
 * - onDeletePlayer: deletes a saved player
 * - onSaveTeam: mark current saved players as baseline and refresh weaknesses
 * - onGetRecommendations: request recommended players from backend
 * - onAddFromSearch, onAddFromRecommendation: add a player from search or recommendations
 */
export function useRecommendations() {
  const [baselineWeakness, setBaselineWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [currentWeakness, setCurrentWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [weaknessLoading, setWeaknessLoading] = useState(false);
  const [weaknessError, setWeaknessError] = useState<string | null>(null);
  const [playerScores, setPlayerScores] = useState<PlayerValueScore[]>([]);

  const [mode, setMode] = useState<PanelMode>("idle");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<SavedPlayer[]>([]);
  const [recommendedPlayers, setRecommendedPlayers] = useState<SavedPlayer[]>([]);
  const [isRecommending, setIsRecommending] = useState(false);
  const [recommendationError, setRecommendationError] = useState("");

  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [playerOperationError, setPlayerOperationError] = useState("");
  const [savingPlayerIds, setSavingPlayerIds] = useState<Set<number>>(new Set());
  const [deletingPlayerIds, setDeletingPlayerIds] = useState<Set<number>>(new Set());
  const latestWeaknessRequest = useRef<symbol | null>(null);
  const lastWeaknessKeysRef = useRef<{ baseline: string; working: string }>({ baseline: "", working: "" });
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [activePosition, setActivePosition] = useState<DiamondPosition>("CF");

  const savedPlayersRef = useRef(savedPlayers);
  const baselineSavedPlayersRef = useRef<SavedPlayer[]>([]);


  // Get all player IDs from saved players (including bench players without positions)
  const getPlayerIdsFromSavedPlayers = useCallback((players: SavedPlayer[]) => {
    return players
      .map((p) => p.id)
      .filter((id): id is number => typeof id === "number");
  }, []);

  const fetchWeaknessFor = useCallback(
    async (players: SavedPlayer[]) => {
      const ids = getPlayerIdsFromSavedPlayers(players);
      if (ids.length === 0) return null;
      const result = await playerActions.getTeamWeakness(ids);
      if (result.success && result.data) return result.data;
      throw new Error(result.error || "Failed to load weaknesses");
    },
    [getPlayerIdsFromSavedPlayers]
  );

  const refreshWeakness = useCallback(
    async (workingOverride?: SavedPlayer[], baselineOverride?: SavedPlayer[]) => {
      const working = workingOverride ?? savedPlayersRef.current;
      const baseline = baselineOverride ?? baselineSavedPlayersRef.current;
      const hasAny =
        getPlayerIdsFromSavedPlayers(working).length > 0 || getPlayerIdsFromSavedPlayers(baseline).length > 0;
      if (!hasAny) {
        setBaselineWeakness(null);
        setCurrentWeakness(null);
        setWeaknessError(null);
        setWeaknessLoading(false);
        latestWeaknessRequest.current = null;
        return;
      }
      const workingIds = getPlayerIdsFromSavedPlayers(working);
      const baselineIds = getPlayerIdsFromSavedPlayers(baseline);
      const workingKey = workingIds.join(",");
      const baselineKey = baselineIds.join(",");
      const unchanged =
        lastWeaknessKeysRef.current.working === workingKey &&
        lastWeaknessKeysRef.current.baseline === baselineKey &&
        !workingOverride &&
        !baselineOverride;
      if (unchanged) {
        return; 
      }
      const requestId = Symbol("weakness");
      latestWeaknessRequest.current = requestId;
      lastWeaknessKeysRef.current = { working: workingKey, baseline: baselineKey };
      setWeaknessLoading(true);
      setWeaknessError(null);
      try {
        const [base, curr] = await Promise.all([
          fetchWeaknessFor(baseline),
          fetchWeaknessFor(working)
        ]);
        if (latestWeaknessRequest.current !== requestId) return;
        setBaselineWeakness(base);
        setCurrentWeakness(curr);
      } catch (e) {
        if (latestWeaknessRequest.current === requestId) {
          setWeaknessError(e instanceof Error ? e.message : "Failed to load weaknesses");
        }
      } finally {
        if (latestWeaknessRequest.current === requestId) {
          latestWeaknessRequest.current = null;
          setWeaknessLoading(false);
        }
      }
    },
    [fetchWeaknessFor, getPlayerIdsFromSavedPlayers]
  );

  useEffect(() => {
    const loadSaved = async () => {
      const res = await playerActions.getSavedPlayers();
      if (res.success && res.data) {
        setSavedPlayers(res.data);
        baselineSavedPlayersRef.current = res.data;
        void refreshWeakness(res.data, res.data);
      } else if (!res.success) {
        setPlayerOperationError(res.error || "Failed to load saved players");
      }
    };
    void loadSaved();
  }, [refreshWeakness]);


  // Watch savedPlayers and trigger weakness refresh when it changes
  useEffect(() => {
    // Update the ref to keep it in sync
    savedPlayersRef.current = savedPlayers;
    
    // Skip if savedPlayers is empty (initial load will be handled by the loadSaved useEffect)
    if (savedPlayers.length === 0 && baselineSavedPlayersRef.current.length === 0) {
      return;
    }
    
    // Pass savedPlayers directly to ensure we use the latest state, not the ref
    // This bypasses the unchanged check and forces a refresh
    // Use savedPlayers for baseline if baseline hasn't been set yet
    const baseline = baselineSavedPlayersRef.current.length > 0 
      ? baselineSavedPlayersRef.current 
      : savedPlayers;
    void refreshWeakness(savedPlayers, baseline);
    
    // Fetch player scores
    const fetchScores = async () => {
      const playerIds = savedPlayers.map(p => p.id).filter((id): id is number => typeof id === 'number');
      if (playerIds.length === 0) {
        setPlayerScores([]);
        return;
      }
      try {
        const res = await playerActions.getPlayerValueScores(playerIds);
        if (res.success && res.data) {
          setPlayerScores(res.data);
        }
      } catch (err) {
        console.error('Failed to fetch player scores:', err);
      }
    };
    void fetchScores();
  }, [savedPlayers, refreshWeakness]);

  const onSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    setMode(value ? "search" : "idle");
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    if (!searchTerm.trim()) {
      setSearchResults([]);
      setMode("idle");
      controller.abort();
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await playerActions.searchPlayers(searchTerm.trim(), controller.signal);
        if (res.success && res.data) {
          setSearchResults(
            res.data.map((p: any) => ({
              id: p.id,
              name: p.name,
              image_url: p.image_url,
              years_active: p.years_active,
            }))
          );
          setMode("search");
        } else if (!res.aborted) {
          setSearchResults([]);
          setMode("idle");
        }
      } catch (err) {
        if (controller.signal.aborted) return;
        setSearchResults([]);
        setMode("idle");
      }
    }, 300);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [searchTerm]);

  const ensurePlayerSaved = useCallback(
    async (player: SavedPlayer) => {
      if (savingPlayerIds.has(player.id) || savedPlayers.some((p) => p.id === player.id)) {
        return true;
      }
      setSavingPlayerIds((prev) => {
        const next = new Set(prev);
        next.add(player.id);
        return next;
      });
      setPlayerOperationError("");
      try {
        const res = await playerActions.addPlayer({
          id: player.id,
          name: player.name,
          image_url: player.image_url,
          years_active: player.years_active,
        });
        if (res.success) {
          setSavedPlayers((prev) => (prev.some((p) => p.id === player.id) ? prev : [...prev, player]));
          return true;
        }
        setPlayerOperationError(res.error || "Failed to save player");
        return false;
      } finally {
        setSavingPlayerIds((prev) => {
          const next = new Set(prev);
          next.delete(player.id);
          return next;
        });
      }
    },
    [savedPlayers, savingPlayerIds]
  );


  const handleAddFromSearch = useCallback(
    (player: SavedPlayer) => {
      void (async () => {
        // Prevent duplication - check if already saved
        const alreadySaved = savedPlayers.some((p) => p.id === player.id);
        
        if (!alreadySaved) {
          const ok = await ensurePlayerSaved(player);
          if (!ok) return;
          // ensurePlayerSaved already updates savedPlayers state, which will trigger the useEffect
          // But we reload to ensure we have the latest data from backend
          const res = await playerActions.getSavedPlayers();
          if (res.success && res.data) {
            setSavedPlayers(res.data);
          }
        }
        
        // Just save to bench (no position assignment) - same as recommendations
        // The savedPlayers state change will trigger the useEffect that calls refreshWeakness
        setMode("idle");
        setSearchTerm("");
      })();
    },
    [ensurePlayerSaved, savedPlayers]
  );

  const handleAddFromRecommendation = useCallback(
    (player: SavedPlayer) => {
      void (async () => {
        // Prevent duplication - check if already saved
        const alreadySaved = savedPlayers.some((p) => p.id === player.id);
        
        if (!alreadySaved) {
          const ok = await ensurePlayerSaved(player);
          if (!ok) return;
          // ensurePlayerSaved already updates savedPlayers state, which will trigger the useEffect
          // But we reload to ensure we have the latest data from backend (in case of any server-side updates)
          const res = await playerActions.getSavedPlayers();
          if (res.success && res.data) {
            setSavedPlayers(res.data);
          }
        }
        
        // Just save to bench (no position assignment) - user can assign position later from saved players section
        // The savedPlayers state change will trigger the useEffect that calls refreshWeakness
        setMode("recommendations");
      })();
    },
    [ensurePlayerSaved, savedPlayers]
  );

  const handleGetRecommendations = useCallback(async () => {
    setRecommendationError("");
    const ids = getPlayerIdsFromSavedPlayers(savedPlayers);
    if (ids.length === 0) {
      setRecommendationError("Add players to your team first.");
      return;
    }
    setIsRecommending(true);
    const res = await playerActions.getRecommendations(ids);
    setIsRecommending(false);
    if (res.success && res.data) {
      setRecommendedPlayers(
        res.data.map((p: any) => ({
          id: p.id,
          name: p.name,
          image_url: p.image_url,
          years_active: p.years_active,
        }))
      );
      setMode("recommendations");
    } else {
      setRecommendationError(res.error || "Failed to fetch recommendations");
      setMode("idle");
    }
  }, [getPlayerIdsFromSavedPlayers, savedPlayers]);


  const savedPlayerIds = useMemo(
    () => new Set(savedPlayers.map((p) => p.id)),
    [savedPlayers]
  );
  // Get IDs of players with positions (starters)
  const assignedIds = useMemo(
    () => new Set(savedPlayers.filter(p => p.position).map(p => p.id)),
    [savedPlayers]
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

        // Update savedPlayers state - this will trigger weakness refresh
        setSavedPlayers((prev) => prev.filter((saved) => saved.id !== player.id));
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

  const prepareDragPlayer = useCallback((player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = player;
    setDraggingId(player.id);
    if (fromPosition) setActivePosition(fromPosition);
  }, []);

  const clearDragState = useCallback(() => {
    dragPlayerRef.current = null;
    setDraggingId(null);
  }, []);


  return {
    mode,
    searchTerm,
    baselineWeakness,
    currentWeakness,
    weaknessLoading,
    weaknessError,
    activePosition,
    draggingId,
    searchResults,
    recommendedPlayers,
    savedPlayers,
    savedPlayerIds,
    assignedIds,
    savingPlayerIds,
    deletingPlayerIds,
    playerScores,
    hasSearchTerm: !!searchTerm.trim(),
    isRecommending,
    recommendationError,
    playerOperationError,
    setSearchTerm: onSearchChange,
    setActivePosition,
    onPrepareDrag: prepareDragPlayer,
    onClearDrag: clearDragState,
    onDeletePlayer: handleDeletePlayer,
    onSaveTeam: () => {
      baselineSavedPlayersRef.current = savedPlayers;
      if (currentWeakness) setBaselineWeakness(currentWeakness);
      void refreshWeakness(savedPlayers, savedPlayers);
    },
    onGetRecommendations: handleGetRecommendations,
    onAddFromSearch: handleAddFromSearch,
    onAddFromRecommendation: handleAddFromRecommendation,
  };
}