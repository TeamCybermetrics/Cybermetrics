import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PageCard } from "@/components";
import WeaknessView from "./components/WeaknessView";
import { playerActions } from "@/actions/players";
import type { SavedPlayer } from "./types";
import type { PlayerValueScore, TeamWeaknessResponse } from "@/api/players";

export default function TeamAnalysisPage() {
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true);
  const [playersError, setPlayersError] = useState<string | null>(null);
  const [weakness, setWeakness] = useState<TeamWeaknessResponse | null>(null);
  const [playerScores, setPlayerScores] = useState<PlayerValueScore[]>([]);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const isMounted = useRef<boolean>(false);
  const analysisRequestId = useRef(0);

  const loadSavedPlayers = async () => {
    setLoadingPlayers(true);
    setPlayersError(null);
    try {
      const result = await playerActions.getSavedPlayers();
      if (!isMounted.current) return;
      if (result.success) {
        setSavedPlayers(result.data || []);
      } else {
        setPlayersError(result.error || "Failed to load players");
      }
    } catch (err) {
      if (!isMounted.current) return;
      setPlayersError(err instanceof Error ? err.message : "Failed to load players");
    } finally {
      if (isMounted.current) {
        setLoadingPlayers(false);
      }
    }
  };

  useEffect(() => {
    isMounted.current = true;
    loadSavedPlayers();
    return () => { isMounted.current = false; };
  }, []);

  const playerIds = useMemo(
    () =>
      savedPlayers
        .map((player) => player.id)
        .filter((id): id is number => typeof id === "number"),
    [savedPlayers]
  );

  const loadAnalysis = useCallback(async (ids: number[]) => {
    const requestId = ++analysisRequestId.current;
    if (ids.length === 0) {
      if (analysisRequestId.current === requestId) {
        setWeakness(null);
        setPlayerScores([]);
        setAnalysisError(null);
      }
      return;
    }

    setLoadingAnalysis(true);
    setAnalysisError(null);

    try {
      const [weaknessRes, scoresRes] = await Promise.all([
        playerActions.getTeamWeakness(ids),
        playerActions.getPlayerValueScores(ids)
      ]);

      if (!isMounted.current || analysisRequestId.current !== requestId) {
        return;
      }

      let errorMessage: string | null = null;

      if (!weaknessRes.success) {
        errorMessage = weaknessRes.error || "Failed to compute team weaknesses";
        setWeakness(null);
      } else {
        setWeakness(weaknessRes.data || null);
      }

      if (!scoresRes.success) {
        const scoreError = scoresRes.error || "Failed to compute player scores";
        errorMessage = errorMessage ? `${errorMessage}; ${scoreError}` : scoreError;
        setPlayerScores([]);
      } else {
        setPlayerScores(scoresRes.data || []);
      }

      if (errorMessage) {
        setAnalysisError(errorMessage);
      }
    } catch (error) {
      if (!isMounted.current || analysisRequestId.current !== requestId) {
        return;
      }
      setAnalysisError(
        error instanceof Error ? error.message : "Failed to analyze lineup"
      );
      setWeakness(null);
      setPlayerScores([]);
    } finally {
      if (isMounted.current && analysisRequestId.current === requestId) {
        setLoadingAnalysis(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!isMounted.current || loadingPlayers) {
      return;
    }

    if (playersError) {
      setWeakness(null);
      setPlayerScores([]);
      setAnalysisError(playersError);
      return;
    }

    if (playerIds.length === 0) {
      setWeakness(null);
      setPlayerScores([]);
      setAnalysisError(null);
      return;
    }

    // Debounce analysis updates to avoid excessive API calls during rapid player changes
    const timer = setTimeout(() => {
      loadAnalysis(playerIds);
    }, 500);

    return () => clearTimeout(timer);
  }, [loadAnalysis, loadingPlayers, playerIds, playersError]);

  const handleRetryAnalysis = useCallback(() => {
    if (playerIds.length === 0) {
      return;
    }
    loadAnalysis(playerIds);
  }, [loadAnalysis, playerIds]);

  const playersWithScores = useMemo(
    () =>
      playerScores.map((score) => {
        const saved = savedPlayers.find((player) => player.id === score.id);
        return {
          ...score,
          image_url: saved?.image_url,
          years_active: saved?.years_active
        };
      }),
    [playerScores, savedPlayers]
  );

  return (
    <PageCard title="Team Analysis">
      <WeaknessView
        weakness={weakness}
        players={playersWithScores}
        loading={loadingAnalysis}
        error={analysisError}
        hasRoster={playerIds.length > 0}
        onRetry={handleRetryAnalysis}
      />
    </PageCard>
  );
}
