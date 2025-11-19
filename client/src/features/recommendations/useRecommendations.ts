import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent } from "react";
import { playerActions } from "@/actions/players";
import type { SavedPlayer, TeamWeaknessResponse } from "@/api/players";
import { LineupState, positionOrder, type DiamondPosition } from "@/components/TeamBuilder/constants";

export type PanelMode = "idle" | "recommendations" | "search";

const emptyLineup: LineupState = positionOrder.reduce(
  (acc, pos) => ({ ...acc, [pos]: null }),
  {} as LineupState
);

export function useRecommendations() {
  const [lineup, setLineup] = useState<LineupState>(emptyLineup);
  const [baselineLineup, setBaselineLineup] = useState<LineupState>(emptyLineup);
  const [baselineWeakness, setBaselineWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [currentWeakness, setCurrentWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [weaknessLoading, setWeaknessLoading] = useState(false);
  const [weaknessError, setWeaknessError] = useState<string | null>(null);

  const [mode, setMode] = useState<PanelMode>("idle");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<SavedPlayer[]>([]);
  const [recommendedPlayers, setRecommendedPlayers] = useState<SavedPlayer[]>([]);
  const [isRecommending, setIsRecommending] = useState(false);
  const [recommendationError, setRecommendationError] = useState("");

  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [playerOperationError, setPlayerOperationError] = useState("");
  const [savingPlayerIds, setSavingPlayerIds] = useState<Set<number>>(new Set());
  const latestWeaknessRequest = useRef<symbol | null>(null);
  const lastWeaknessKeysRef = useRef<{ baseline: string; working: string }>({ baseline: "", working: "" });
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [activePosition, setActivePosition] = useState<DiamondPosition>("CF");

  const lineupRef = useRef(lineup);
  const baselineLineupRef = useRef(baselineLineup);

  const getPlayerIdsFromLineup = useCallback((state: LineupState) => {
    return positionOrder
      .map((pos) => state[pos]?.id)
      .filter((id): id is number => typeof id === "number");
  }, []);

  const fetchWeaknessFor = useCallback(
    async (state: LineupState) => {
      const ids = getPlayerIdsFromLineup(state);
      if (ids.length === 0) return null;
      const result = await playerActions.getTeamWeakness(ids);
      if (result.success && result.data) return result.data;
      throw new Error(result.error || "Failed to load weaknesses");
    },
    [getPlayerIdsFromLineup]
  );

  const refreshWeakness = useCallback(
    async (workingOverride?: LineupState, baselineOverride?: LineupState) => {
      const requestId = Symbol("weakness");
      latestWeaknessRequest.current = requestId;

      const working = workingOverride ?? lineupRef.current;
      const baseline = baselineOverride ?? baselineLineupRef.current;
      const hasAny =
        getPlayerIdsFromLineup(working).length > 0 || getPlayerIdsFromLineup(baseline).length > 0;
      if (!hasAny) {
        setBaselineWeakness(null);
        setCurrentWeakness(null);
        setWeaknessError(null);
        setWeaknessLoading(false);
        latestWeaknessRequest.current = null;
        return;
      }
      const workingIds = getPlayerIdsFromLineup(working);
      const baselineIds = getPlayerIdsFromLineup(baseline);
      const workingKey = workingIds.join(",");
      const baselineKey = baselineIds.join(",");
      if (
        lastWeaknessKeysRef.current.working === workingKey &&
        lastWeaknessKeysRef.current.baseline === baselineKey &&
        !workingOverride &&
        !baselineOverride
      ) {
        return;
      }
      lastWeaknessKeysRef.current = { working: workingKey, baseline: baselineKey };
      setWeaknessLoading(true);
      setWeaknessError(null);
      try {
        const [base, curr] = await Promise.all([fetchWeaknessFor(baseline), fetchWeaknessFor(working)]);
        if (latestWeaknessRequest.current !== requestId) {
          return;
        }
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
    [fetchWeaknessFor, getPlayerIdsFromLineup]
  );

  useEffect(() => {
    lineupRef.current = lineup;
  }, [lineup]);

  useEffect(() => {
    baselineLineupRef.current = baselineLineup;
  }, [baselineLineup]);

  useEffect(() => {
    const loadSaved = async () => {
      const res = await playerActions.getSavedPlayers();
      if (res.success && res.data) {
        setSavedPlayers(res.data);
        const next: LineupState = positionOrder.reduce(
          (acc, pos) => ({ ...acc, [pos]: null }),
          {} as LineupState
        );
        res.data.forEach((p) => {
          if (p.position && positionOrder.includes(p.position as DiamondPosition)) {
            next[p.position as DiamondPosition] = p;
          }
        });
        setLineup(next);
        setBaselineLineup(next);
        void refreshWeakness(next, next);
      } else if (!res.success) {
        setPlayerOperationError(res.error || "Failed to load saved players");
      }
    };
    void loadSaved();
  }, [refreshWeakness]);

  useEffect(() => {
    void refreshWeakness();
  }, [lineup, baselineLineup, refreshWeakness]);

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

  const assignPlayerToLineup = useCallback(
    (player: SavedPlayer, position?: DiamondPosition) => {
      const target = position ?? activePosition;
      setLineup((prev) => {
        const next: LineupState = { ...prev };
        positionOrder.forEach((pos) => {
          if (next[pos]?.id === player.id) next[pos] = null;
        });
        next[target] = player;
        return next;
      });
      setActivePosition(target);
    },
    [activePosition]
  );

  const handleAddFromSearch = useCallback(
    (player: SavedPlayer) => {
      void (async () => {
        const ok = await ensurePlayerSaved(player);
        if (ok) {
          assignPlayerToLineup(player);
          setMode("idle");
          setSearchTerm("");
        }
      })();
    },
    [assignPlayerToLineup, ensurePlayerSaved]
  );

  const handleAddFromRecommendation = useCallback(
    (player: SavedPlayer, position?: DiamondPosition) => {
      void (async () => {
        const ok = await ensurePlayerSaved(player);
        if (ok) {
          assignPlayerToLineup(player, position);
          setMode("recommendations");
        }
      })();
    },
    [assignPlayerToLineup, ensurePlayerSaved]
  );

  const handleGetRecommendations = useCallback(async () => {
    setRecommendationError("");
    const ids = getPlayerIdsFromLineup(lineup);
    if (ids.length === 0) {
      setRecommendationError("Select players to build your lineup first.");
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
  }, [getPlayerIdsFromLineup, lineup]);

  const handleClearSlot = useCallback(
    (position: DiamondPosition) => {
      setLineup((prev) => ({ ...prev, [position]: null }));
    },
    []
  );

  const savedPlayerIds = useMemo(
    () => new Set(savedPlayers.map((p) => p.id)),
    [savedPlayers]
  );
  const assignedIds = useMemo(
    () => new Set(getPlayerIdsFromLineup(lineup)),
    [lineup, getPlayerIdsFromLineup]
  );

  const prepareDragPlayer = useCallback((player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = player;
    setDraggingId(player.id);
    if (fromPosition) setActivePosition(fromPosition);
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

  return {
    mode,
    searchTerm,
    lineup,
    baselineLineup,
    baselineWeakness,
    currentWeakness,
    weaknessLoading,
    weaknessError,
    activePosition,
    dropTarget,
    draggingId,
    searchResults,
    recommendedPlayers,
    savedPlayerIds,
    assignedIds,
    savingPlayerIds,
    hasSearchTerm: !!searchTerm.trim(),
    isRecommending,
    recommendationError,
    playerOperationError,
    setSearchTerm: onSearchChange,
    setActivePosition,
    setDropTarget,
    onClearSlot: handleClearSlot,
    onPrepareDrag: prepareDragPlayer,
    onClearDrag: clearDragState,
    onPositionDrop: handlePositionDrop,
    onSaveTeam: () => {
      setBaselineLineup(lineup);
      if (currentWeakness) setBaselineWeakness(currentWeakness);
      void refreshWeakness(lineup, lineup);
    },
    onGetRecommendations: handleGetRecommendations,
    onAddFromSearch: handleAddFromSearch,
    onAddFromRecommendation: handleAddFromRecommendation,
  };
}
