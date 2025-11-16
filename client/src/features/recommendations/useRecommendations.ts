import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent } from "react";
import { playerActions } from "@/actions/players";
import type { PlayerSearchResult, SavedPlayer } from "@/api/players";
import {
  DiamondPosition,
  LineupState,
  SavedTeam,
  positionOrder,
} from "@/components/TeamBuilder/constants";

export type PanelMode = "idle" | "recommendations" | "search";

export function useRecommendations() {
  // ✅ ALL useState
  const [lineup, setLineup] = useState<LineupState>(() =>
    positionOrder.reduce((acc, position) => ({ ...acc, [position]: null }), {} as LineupState)
  );
  const lineupRef = useRef(lineup);
  const [activePosition, setActivePosition] = useState<DiamondPosition | null>("CF");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [savedPlayersLoaded, setSavedPlayersLoaded] = useState(false);
  const searchControllerRef = useRef<AbortController | null>(null);
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [teamName] = useState("TeamName1");
  const [savedTeams, setSavedTeams] = useState<SavedTeam[]>([]);
  const [recommendedPlayers, setRecommendedPlayers] = useState<PlayerSearchResult[]>([]);
  const [recommendationError, setRecommendationError] = useState("");
  const [isRecommending, setIsRecommending] = useState(false);
  const [savingPlayerIds, setSavingPlayerIds] = useState<Set<number>>(() => new Set());
  const [deletingPlayerIds, setDeletingPlayerIds] = useState<Set<number>>(() => new Set());
  const [playerOperationError, setPlayerOperationError] = useState("");
  const [mode, setMode] = useState<PanelMode>("idle");

  useEffect(() => {
    lineupRef.current = lineup;
  }, [lineup]);

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

  useEffect(() => {
    return () => {
      searchControllerRef.current?.abort();
    };
  }, []);


  const performSearch = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) {
      searchControllerRef.current?.abort();
      searchControllerRef.current = null;
      setSearchResults([]);
      setMode("idle");
      return;
    }
    searchControllerRef.current?.abort();
    const controller = new AbortController();
    searchControllerRef.current = controller;
    const result = await playerActions.searchPlayers(trimmed, controller.signal);
    if (searchControllerRef.current !== controller) return;
    if (result.success && result.data) {
      setSearchResults(result.data);
      setMode("search");
      searchControllerRef.current = null;
      return;
    }
    if (result.aborted) {
      searchControllerRef.current = null;
      return;
    }
    setSearchResults([]);
    setPlayerOperationError(result.error || "Search failed");
    setMode("idle");
    searchControllerRef.current = null;
  }, []);

  const buildLineupFromSavedPlayers = useCallback((players: SavedPlayer[]) => {
    return positionOrder.reduce((acc, position) => {
      const playerForSlot = players.find((saved) => saved.position === position) || null;
      acc[position] = playerForSlot;
      return acc;
    }, {} as LineupState);
  }, []);

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

  const persistPlayerPosition = useCallback(
    async (playerId: number, position: DiamondPosition | null) => {
      const result = await playerActions.updatePlayerPosition(playerId, position);
      if (result.success && result.data) {
        setPlayerOperationError("");
        setSavedPlayers((prev) => {
          const index = prev.findIndex((saved) => saved.id === playerId);
          if (index === -1) return [...prev, result.data];
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
          if (next[slot]?.id === player.id) next[slot] = null;
        });
        next[position] = player;
        return next;
      });

      setActivePosition(position);

      setSavedPlayers((prev) => {
        const updated = prev.map((saved) => {
          if (saved.id === player.id) return { ...saved, position };
          if (replacedPlayer && saved.id === replacedPlayer.id && replacedPlayer.id !== player.id) {
            return { ...saved, position: null };
          }
          return saved;
        });
        if (!prev.some((saved) => saved.id === player.id)) {
          updated.push({ ...player, position });
        }
        if (replacedPlayer && replacedPlayer.id !== player.id && !prev.some((saved) => saved.id === replacedPlayer.id)) {
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
      if (!activePosition) return;
      setPlayerOperationError("");
      setSavingPlayerIds((prev) => {
        const next = new Set(prev);
        next.add(player.id);
        return next;
      });
      try {
        const saved = await ensurePlayerIsSaved(player);
        if (saved) assignPlayerToPosition(player, activePosition);
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
            if (prev.some((existing) => existing.id === player.id)) return prev;
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

  useEffect(() => {
    const timer = setTimeout(() => {
      void performSearch(searchTerm);
    }, 250);
    return () => clearTimeout(timer);
  }, [performSearch, searchTerm]);

  useEffect(() => {
    if (!savedPlayersLoaded) return;
    const nextLineup = buildLineupFromSavedPlayers(savedPlayers);
    setLineup((prev) => {
      const hasChanges = positionOrder.some(
        (position) => (prev[position]?.id ?? null) !== (nextLineup[position]?.id ?? null)
      );
      return hasChanges ? nextLineup : prev;
    });
  }, [savedPlayers, savedPlayersLoaded, buildLineupFromSavedPlayers]);


  const handleClearSlot = (position: DiamondPosition) => {
    const player = lineupRef.current[position];
    if (!player) return;
    setLineup((prev) => ({ ...prev, [position]: null }));
    setSavedPlayers((prev) => {
      const found = prev.some((saved) => saved.id === player.id);
      if (!found) return [...prev, { ...player, position: null }];
      return prev.map((saved) =>
        saved.id === player.id ? { ...saved, position: null } : saved
      );
    });
    void persistPlayerPosition(player.id, null);
  };

  const prepareDragPlayer = (player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = { ...player };
    setDraggingId(player.id);
    if (fromPosition) setActivePosition(fromPosition);
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
      if (saved) assignPlayerToPosition(player, position);
    } finally {
      clearDragState();
    }
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

  const handleGetRecommendations = async () => {
    setRecommendationError("");
    setMode("recommendations");
    
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


  const trimmedSearchTerm = searchTerm.trim();
  const hasSearchTerm = trimmedSearchTerm.length > 0;

  const searchResultPlayers = useMemo(() => {
    if (!hasSearchTerm) return [];
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

  return {
    mode,
    searchTerm,
    lineup,
    activePosition,
    dropTarget,
    draggingId,
    savedPlayers,
    searchResultPlayers,
    recommendedPlayers,
    savedPlayerIds,
    assignedIds,
    savingPlayerIds,
    deletingPlayerIds,
    hasSearchTerm,
    isRecommending,
    recommendationError,
    playerOperationError,
    isRosterComplete,
    incompletePositions,
    setSearchTerm,
    setActivePosition,
    setDropTarget,
    handleAddPlayer,
    handleDeletePlayer,
    handleSavePlayerOnly,
    handleClearSlot,
    prepareDragPlayer,
    clearDragState,
    handlePositionDrop,
    saveTeam,
    handleGetRecommendations,
  };
}