import type { PanelMode } from "./useRecommendations";
import type { TeamWeaknessResponse, SavedPlayer, PlayerValueScore } from "@/api/players";
import type { DiamondPosition } from "@/components/TeamBuilder/constants";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { RecommendationsSection } from "@/components/Recommendations/RecommendationsSection/RecommendationsSection";
import { SavedPlayersSection } from "@/components/TeamBuilder/SavedPlayersSection/SavedPlayersSection";
import { formatZScore } from "@/utils/zScoreRadar";
import { Card } from "@/components";
import { RecommendationsRadarCard } from "@/components/Recommendations/RecommendationsRadarCard";
import styles from "./RecommendationsView.module.css";

type Props = {
  mode: PanelMode;
  searchTerm: string;
  draggingId: number | null;
  searchResults: SavedPlayer[];
  recommendedPlayers: SavedPlayer[];
  savedPlayers: SavedPlayer[];
  savedPlayerIds: Set<number>;
  assignedIds: Set<number>;
  savingPlayerIds: Set<number>;
  deletingPlayerIds: Set<number>;
  playerScores: PlayerValueScore[];
  hasSearchTerm: boolean;
  isRecommending: boolean;
  recommendationError: string;
  playerOperationError: string;
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  weaknessLoading: boolean;
  weaknessError: string | null;
  setSearchTerm: (v: string) => void;
  onPrepareDrag: (player: SavedPlayer, fromPosition?: DiamondPosition) => void;
  onClearDrag: () => void;
  onDeletePlayer: (player: SavedPlayer) => void | Promise<void>;
  onSaveTeam: () => void;
  onGetRecommendations: () => void;
  onAddFromSearch: (player: SavedPlayer) => void;
  onAddFromRecommendation: (player: SavedPlayer) => void;
};

const STAT_KEYS: { key: keyof TeamWeaknessResponse; label: string }[] = [
  { key: "strikeout_rate", label: "Strikeout Rate" },
  { key: "walk_rate", label: "Walk Rate" },
  { key: "isolated_power", label: "Iso Power" },
  { key: "on_base_percentage", label: "On Base %" },
  { key: "base_running", label: "Base Running" },
];

const formatValueNumber = (value: number) => formatZScore(value, 2);

/**
 * Render the recommendations view that displays saved players, a weaknesses radar, search controls, and recommended players.
 *
 * @param mode - Current panel mode: "idle", "search", or "recommendations"
 * @param searchTerm - Current search input value
 * @param draggingId - ID of the player currently being dragged, if any
 * @param searchResults - Players matching the current search
 * @param recommendedPlayers - Players produced by the recommendation engine
 * @param savedPlayers - Players saved to the user's team
 * @param savedPlayerIds - Set of IDs for players already saved to the team
 * @param assignedIds - Set of player IDs already assigned to lineup slots
 * @param savingPlayerIds - Set of player IDs currently being saved
 * @param deletingPlayerIds - Set of player IDs currently being deleted
 * @param playerScores - Array of per-player value scores used for display
 * @param hasSearchTerm - Whether the search input contains text
 * @param isRecommending - Whether a recommendation request is in progress
 * @param recommendationError - Error message from the recommendation request, if any
 * @param playerOperationError - Error message from player search/save/delete operations, if any
 * @param baselineWeakness - Weakness profile for the saved baseline team, if set
 * @param currentWeakness - Weakness profile for the current team, if available
 * @param weaknessLoading - Whether weakness data is loading
 * @param weaknessError - Error message for weakness data, if any
 * @param setSearchTerm - Handler to update the search term
 * @param onPrepareDrag - Handler called to begin dragging a player
 * @param onClearDrag - Handler called to clear drag state
 * @param onDeletePlayer - Handler to delete a saved player
 * @param onSaveTeam - Handler to set the current saved players as the baseline team
 * @param onGetRecommendations - Handler to trigger fetching recommendations
 * @param onAddFromSearch - Handler to save a player from search results
 * @param onAddFromRecommendation - Handler to save a player from recommendations
 * @returns The rendered RecommendationsView component
 */
export function RecommendationsView({
  mode,
  searchTerm,
  draggingId,
  searchResults,
  recommendedPlayers,
  savedPlayers,
  savedPlayerIds,
  assignedIds,
  savingPlayerIds,
  deletingPlayerIds,
  playerScores,
  hasSearchTerm,
  isRecommending,
  recommendationError,
  playerOperationError,
  baselineWeakness,
  currentWeakness,
  weaknessLoading,
  weaknessError,
  setSearchTerm,
  onPrepareDrag,
  onClearDrag,
  onDeletePlayer,
  onSaveTeam,
  onGetRecommendations,
  onAddFromSearch,
  onAddFromRecommendation,
}: Props) {
  const EPS = 1e-3;
  let highlightOrder: number[] = [];
  if (baselineWeakness && currentWeakness) {
    const deltas = STAT_KEYS.map(({ key }) => currentWeakness[key] - baselineWeakness[key]);
    const hasMeaningfulDelta = deltas.some((d) => Math.abs(d) > EPS);
    if (hasMeaningfulDelta) {
      highlightOrder = deltas
        .map((delta, idx) => ({ delta, idx }))
        .sort((a, b) => a.delta - b.delta)
        .map((entry) => entry.idx)
        .slice(0, 2);
    }
  } else if (currentWeakness) {
    const values = STAT_KEYS.map(({ key }) => currentWeakness[key]);
    const hasVariation = values.some((v) => Math.abs(v) > EPS);
    if (hasVariation) {
      highlightOrder = values
        .map((value, idx) => ({ value, idx }))
        .sort((a, b) => a.value - b.value)
        .map((entry) => entry.idx)
        .slice(0, 2);
    }
  }

  return (
    <div className={styles.layout}>
      {/* Left column - Saved Players */}
      <div className={styles.leftCol}>
        <SavedPlayersSection
          players={savedPlayers}
          assignedIds={assignedIds}
          draggingId={draggingId}
          deletingPlayerIds={deletingPlayerIds}
          onPrepareDrag={onPrepareDrag}
          onClearDrag={onClearDrag}
          onDeletePlayer={onDeletePlayer}
          playerScores={playerScores}
          headerAction={
            <div className={styles.baselineAction}>
              <div className={styles.baselineDescription}>Set current team as baseline</div>
              <button className={styles.baselineBtn} onClick={onSaveTeam}>
                Set Baseline
              </button>
            </div>
          }
        />
      </div>

      {/* Right column - Search and Recommendations */}
      <div className={styles.rightCol}>
        <RecommendationsRadarCard
          statKeys={STAT_KEYS}
          baselineWeakness={baselineWeakness}
          currentWeakness={currentWeakness}
          highlightOrder={highlightOrder}
          loading={weaknessLoading}
          error={weaknessError}
          formatValue={formatValueNumber}
        />

        {/* Get Recommendations button */}
        <Card title="Get Recommendations">
          <button className={styles.ctaBtn} onClick={onGetRecommendations} disabled={isRecommending}>
            {isRecommending ? "Loading..." : "Get Recommendations!"}
          </button>
          {recommendationError && <div className={styles.recommendError}>{recommendationError}</div>}
        </Card>

        {/* Search bar */}
        <Card title="Search Players">
          <SearchBar
            searchTerm={searchTerm}
            onSearchTermChange={setSearchTerm}
            statusText={
              hasSearchTerm
                ? `${searchResults.length} results`
                : ""
            }
            errorMessage={playerOperationError || undefined}
          />
        </Card>

        {mode === "search" && (
          <SearchResultsSection
            players={searchResults}
            savedPlayerIds={savedPlayerIds}
            assignedIds={assignedIds}
            draggingId={draggingId}
            savingPlayerIds={savingPlayerIds}
            deletingPlayerIds={deletingPlayerIds}
            onPrepareDrag={onPrepareDrag}
            onClearDrag={onClearDrag}
            onSavePlayer={onAddFromSearch}
            onDeletePlayer={onDeletePlayer}
          />
        )}

        {mode === "recommendations" && (
          <RecommendationsSection
            players={recommendedPlayers}
            savedPlayerIds={savedPlayerIds}
            savingPlayerIds={savingPlayerIds}
            deletingPlayerIds={deletingPlayerIds}
            allowAddSaved
            addLabel="Save to Team"
            onSavePlayer={(player) => onAddFromRecommendation(player)}
            onDeletePlayer={onDeletePlayer}
          />
        )}

        {mode === "idle" && (
          <div className={styles.displayPanel}>
            <div className={styles.placeholder}>
              Use the search bar or click "Get Recommendations!" to see players.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

