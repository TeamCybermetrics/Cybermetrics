import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PageCard } from "@/components";
import WeaknessView from "./components/WeaknessView";
import { playerActions } from "@/actions/players";
import type { SavedPlayer } from "./types";
import type { PlayerValueScore, TeamWeaknessResponse } from "@/api/players";

/**
 * Displays a team analysis UI that computes and shows team weaknesses and player value scores
 * for either the active lineup or the full roster, with independent loading and error states.
 *
 * The component loads saved players, derives active and full roster IDs, debounces analysis requests,
 * and runs separate API-driven analyses (weaknesses and player scores) for each mode; users can toggle
 * between "Active Lineup" and "Full Roster" and retry the current analysis.
 *
 * @returns A React element containing the team analysis page with mode toggles and a WeaknessView populated with the current analysis state
 */
export default function TeamAnalysisPage() {
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true);
  const [playersError, setPlayersError] = useState<string | null>(null);
  
  // Analysis for active lineup (9 players in positions)
  const [activeLineupWeakness, setActiveLineupWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [activeLineupScores, setActiveLineupScores] = useState<PlayerValueScore[]>([]);
  const [loadingActiveAnalysis, setLoadingActiveAnalysis] = useState(false);
  const [activeAnalysisError, setActiveAnalysisError] = useState<string | null>(null);
  
  // Analysis for full roster (all saved players)
  const [fullRosterWeakness, setFullRosterWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [fullRosterScores, setFullRosterScores] = useState<PlayerValueScore[]>([]);
  const [loadingFullAnalysis, setLoadingFullAnalysis] = useState(false);
  const [fullAnalysisError, setFullAnalysisError] = useState<string | null>(null);
  
  const [analysisMode, setAnalysisMode] = useState<"active" | "full">("active");
  const isMounted = useRef<boolean>(false);
  const activeAnalysisRequestId = useRef(0);
  const fullAnalysisRequestId = useRef(0);

  const loadSavedPlayers = async () => {
    setLoadingPlayers(true);
    setPlayersError(null);
    try {
      const result = await playerActions.getSavedPlayers();
      if (!isMounted.current) return;
      if (result.success) {
        console.log("Loaded saved players:", result.data);
        setSavedPlayers(result.data || []);
      } else {
        setPlayersError(result.error || "Failed to load players");
      }
    } catch (err) {
      if (!isMounted.current) return;
      setPlayersError(err instanceof Error ? err.message : "Failed to load players");
    } finally {
      if (isMounted.current) {
        console.log("Finished loading players, setting loadingPlayers to false");
        setLoadingPlayers(false);
      }
    }
  };

  useEffect(() => {
    isMounted.current = true;
    loadSavedPlayers();
    return () => { isMounted.current = false; };
  }, []);

  // Get IDs for active lineup (only players with positions)
  const activeLineupIds = useMemo(
    () => {
      const ids = savedPlayers
        .filter((player) => player.position != null && player.position !== "")
        .map((player) => player.id)
        .filter((id): id is number => typeof id === "number");
      console.log("Active lineup IDs:", ids, "from", savedPlayers.filter(p => p.position != null && p.position !== ""));
      return ids;
    },
    [savedPlayers]
  );
  
  // Get IDs for full roster (all saved players)
  const fullRosterIds = useMemo(
    () => {
      const ids = savedPlayers
        .map((player) => player.id)
        .filter((id): id is number => typeof id === "number");
      console.log("Full roster IDs:", ids, "from", savedPlayers.length, "players");
      return ids;
    },
    [savedPlayers]
  );

  const loadActiveAnalysis = async (ids: number[]) => {
    console.log(`Loading active analysis for IDs:`, ids);
    const requestId = ++activeAnalysisRequestId.current;
    
    if (ids.length === 0) {
      console.log(`No IDs for active analysis, skipping`);
      if (activeAnalysisRequestId.current === requestId) {
        setActiveLineupWeakness(null);
        setActiveLineupScores([]);
        setActiveAnalysisError(null);
      }
      return;
    }

    setLoadingActiveAnalysis(true);
    setActiveAnalysisError(null);
    console.log(`Starting active analysis API calls...`);

    try {
      const [weaknessRes, scoresRes] = await Promise.all([
        playerActions.getTeamWeakness(ids),
        playerActions.getPlayerValueScores(ids)
      ]);

      if (!isMounted.current || activeAnalysisRequestId.current !== requestId) {
        console.log("Active analysis cancelled");
        return;
      }

      let errorMessage: string | null = null;

      if (!weaknessRes.success) {
        errorMessage = weaknessRes.error || "Failed to compute team weaknesses";
        setActiveLineupWeakness(null);
      } else {
        console.log("Active weakness analysis succeeded");
        setActiveLineupWeakness(weaknessRes.data || null);
      }

      if (!scoresRes.success) {
        const scoreError = scoresRes.error || "Failed to compute player scores";
        errorMessage = errorMessage ? `${errorMessage}; ${scoreError}` : scoreError;
        setActiveLineupScores([]);
      } else {
        console.log("Active scores analysis succeeded:", scoresRes.data?.length);
        setActiveLineupScores(scoresRes.data || []);
      }

      if (errorMessage) {
        setActiveAnalysisError(errorMessage);
      }
      console.log("Active analysis completed");
    } catch (error) {
      console.error("Active analysis error:", error);
      if (!isMounted.current || activeAnalysisRequestId.current !== requestId) {
        return;
      }
      setActiveAnalysisError(
        error instanceof Error ? error.message : "Failed to analyze lineup"
      );
      setActiveLineupWeakness(null);
      setActiveLineupScores([]);
    } finally {
      if (isMounted.current && activeAnalysisRequestId.current === requestId) {
        console.log("Active analysis setting loading to false");
        setLoadingActiveAnalysis(false);
      }
    }
  };

  const loadFullAnalysis = async (ids: number[]) => {
    console.log(`Loading full analysis for IDs:`, ids);
    const requestId = ++fullAnalysisRequestId.current;
    
    if (ids.length === 0) {
      console.log(`No IDs for full analysis, skipping`);
      if (fullAnalysisRequestId.current === requestId) {
        setFullRosterWeakness(null);
        setFullRosterScores([]);
        setFullAnalysisError(null);
      }
      return;
    }

    setLoadingFullAnalysis(true);
    setFullAnalysisError(null);
    console.log(`Starting full analysis API calls...`);

    try {
      const [weaknessRes, scoresRes] = await Promise.all([
        playerActions.getTeamWeakness(ids),
        playerActions.getPlayerValueScores(ids)
      ]);

      if (!isMounted.current || fullAnalysisRequestId.current !== requestId) {
        console.log("Full analysis cancelled");
        return;
      }

      let errorMessage: string | null = null;

      if (!weaknessRes.success) {
        errorMessage = weaknessRes.error || "Failed to compute team weaknesses";
        setFullRosterWeakness(null);
      } else {
        console.log("Full weakness analysis succeeded");
        setFullRosterWeakness(weaknessRes.data || null);
      }

      if (!scoresRes.success) {
        const scoreError = scoresRes.error || "Failed to compute player scores";
        errorMessage = errorMessage ? `${errorMessage}; ${scoreError}` : scoreError;
        setFullRosterScores([]);
      } else {
        console.log("Full scores analysis succeeded:", scoresRes.data?.length);
        setFullRosterScores(scoresRes.data || []);
      }

      if (errorMessage) {
        setFullAnalysisError(errorMessage);
      }
      console.log("Full analysis completed");
    } catch (error) {
      console.error("Full analysis error:", error);
      if (!isMounted.current || fullAnalysisRequestId.current !== requestId) {
        return;
      }
      setFullAnalysisError(
        error instanceof Error ? error.message : "Failed to analyze lineup"
      );
      setFullRosterWeakness(null);
      setFullRosterScores([]);
    } finally {
      if (isMounted.current && fullAnalysisRequestId.current === requestId) {
        console.log("Full analysis setting loading to false");
        setLoadingFullAnalysis(false);
      }
    }
  };

  // Load active lineup analysis
  useEffect(() => {
    console.log("Active lineup effect triggered. loadingPlayers:", loadingPlayers, "activeLineupIds:", activeLineupIds);
    if (loadingPlayers) {
      console.log("Still loading players, skipping active analysis");
      return;
    }

    if (playersError) {
      console.log("Players error, clearing active analysis:", playersError);
      setActiveLineupWeakness(null);
      setActiveLineupScores([]);
      setActiveAnalysisError(playersError);
      return;
    }

    if (activeLineupIds.length === 0) {
      console.log("No active lineup players, clearing active analysis");
      setActiveLineupWeakness(null);
      setActiveLineupScores([]);
      setActiveAnalysisError(null);
      return;
    }

    console.log("Scheduling active lineup analysis in 500ms");
    // Debounce analysis updates to avoid excessive API calls during rapid player changes
    const timer = setTimeout(() => {
      loadActiveAnalysis(activeLineupIds);
    }, 500);

    return () => clearTimeout(timer);
  }, [loadingPlayers, activeLineupIds, playersError]);
  
  // Load full roster analysis
  useEffect(() => {
    console.log("Full roster effect triggered. loadingPlayers:", loadingPlayers, "fullRosterIds:", fullRosterIds);
    if (loadingPlayers) {
      console.log("Still loading players, skipping full roster analysis");
      return;
    }

    if (playersError) {
      console.log("Players error, clearing full roster analysis:", playersError);
      setFullRosterWeakness(null);
      setFullRosterScores([]);
      setFullAnalysisError(playersError);
      return;
    }

    if (fullRosterIds.length === 0) {
      console.log("No full roster players, clearing full roster analysis");
      setFullRosterWeakness(null);
      setFullRosterScores([]);
      setFullAnalysisError(null);
      return;
    }

    console.log("Scheduling full roster analysis in 500ms");
    // Debounce analysis updates to avoid excessive API calls during rapid player changes
    const timer = setTimeout(() => {
      loadFullAnalysis(fullRosterIds);
    }, 500);

    return () => clearTimeout(timer);
  }, [loadingPlayers, fullRosterIds, playersError]);

  const handleRetryAnalysis = useCallback(() => {
    if (analysisMode === "active") {
      if (activeLineupIds.length === 0) {
        return;
      }
      loadActiveAnalysis(activeLineupIds);
    } else {
      if (fullRosterIds.length === 0) {
        return;
      }
      loadFullAnalysis(fullRosterIds);
    }
  }, [activeLineupIds, fullRosterIds, analysisMode]);

  const activePlayersWithScores = useMemo(
    () =>
      activeLineupScores.map((score) => {
        const saved = savedPlayers.find((player) => player.id === score.id);
        return {
          ...score,
          image_url: saved?.image_url,
          years_active: saved?.years_active
        };
      }),
    [activeLineupScores, savedPlayers]
  );
  
  const fullRosterPlayersWithScores = useMemo(
    () =>
      fullRosterScores.map((score) => {
        const saved = savedPlayers.find((player) => player.id === score.id);
        return {
          ...score,
          image_url: saved?.image_url,
          years_active: saved?.years_active
        };
      }),
    [fullRosterScores, savedPlayers]
  );

  const currentWeakness = analysisMode === "active" ? activeLineupWeakness : fullRosterWeakness;
  const currentPlayers = analysisMode === "active" ? activePlayersWithScores : fullRosterPlayersWithScores;
  const currentLoading = analysisMode === "active" ? loadingActiveAnalysis : loadingFullAnalysis;
  const currentError = analysisMode === "active" ? activeAnalysisError : fullAnalysisError;
  const currentPlayerCount = analysisMode === "active" ? activeLineupIds.length : fullRosterIds.length;

  return (
    <PageCard title="Team Analysis">
      <div style={{ marginBottom: "1.5rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <button
          onClick={() => setAnalysisMode("active")}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "0.375rem",
            border: "1px solid",
            borderColor: analysisMode === "active" ? "#6d7bff" : "rgba(255,255,255,0.2)",
            backgroundColor: analysisMode === "active" ? "rgba(109,123,255,0.2)" : "transparent",
            color: "white",
            cursor: "pointer",
            fontWeight: analysisMode === "active" ? "600" : "400",
            transition: "all 0.2s"
          }}
        >
          Active Lineup ({activeLineupIds.length} players)
        </button>
        <button
          onClick={() => setAnalysisMode("full")}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "0.375rem",
            border: "1px solid",
            borderColor: analysisMode === "full" ? "#6d7bff" : "rgba(255,255,255,0.2)",
            backgroundColor: analysisMode === "full" ? "rgba(109,123,255,0.2)" : "transparent",
            color: "white",
            cursor: "pointer",
            fontWeight: analysisMode === "full" ? "600" : "400",
            transition: "all 0.2s"
          }}
        >
          Full Roster ({fullRosterIds.length} players)
        </button>
      </div>
      <WeaknessView
        weakness={currentWeakness}
        players={currentPlayers}
        loading={currentLoading}
        error={currentError}
        hasRoster={currentPlayerCount > 0}
        onRetry={handleRetryAnalysis}
      />
    </PageCard>
  );
}