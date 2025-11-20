import type { PanelMode } from "./useRecommendations";
import type { TeamWeaknessResponse, SavedPlayer } from "@/api/players";
import type { DiamondPosition } from "@/components/TeamBuilder/constants";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { RecommendationsSection } from "@/components/Recommendations/RecommendationsSection/RecommendationsSection";
import { SavedPlayersSection } from "@/components/TeamBuilder/SavedPlayersSection/SavedPlayersSection";
import { formatZScore } from "@/utils/zScoreRadar";
import { Card } from "@/components";
import { WeaknessDeltasCard } from "@/components/Recommendations/WeaknessDeltasCard";
import { RecommendationsRadarCard } from "@/components/Recommendations/RecommendationsRadarCard";
import styles from "./RecommendationsView.module.css";

type Props = {
  mode: PanelMode;
  searchTerm: string;
  activePosition: DiamondPosition;
  draggingId: number | null;
  searchResults: SavedPlayer[];
  recommendedPlayers: SavedPlayer[];
  savedPlayers: SavedPlayer[];
  savedPlayerIds: Set<number>;
  assignedIds: Set<number>;
  savingPlayerIds: Set<number>;
  deletingPlayerIds: Set<number>;
  hasSearchTerm: boolean;
  isRecommending: boolean;
  recommendationError: string;
  playerOperationError: string;
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  weaknessLoading: boolean;
  weaknessError: string | null;
  setSearchTerm: (v: string) => void;
  setActivePosition: (pos: DiamondPosition) => void;
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

export function RecommendationsView({
  mode,
  searchTerm,
  activePosition,
  draggingId,
  searchResults,
  recommendedPlayers,
  savedPlayers,
  savedPlayerIds,
  assignedIds,
  savingPlayerIds,
  deletingPlayerIds,
  hasSearchTerm,
  isRecommending,
  recommendationError,
  playerOperationError,
  baselineWeakness,
  currentWeakness,
  weaknessLoading,
  weaknessError,
  setSearchTerm,
  setActivePosition,
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
      {/* Left column */}
      <div className={styles.leftCol}>
        {/* Deltas */}
        <WeaknessDeltasCard
          statKeys={STAT_KEYS}
          baselineWeakness={baselineWeakness}
          currentWeakness={currentWeakness}
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

        {/* Set Baseline button */}
        <Card title="Baseline Comparison">
          <p className={styles.description}>Set current team as baseline for comparison.</p>
          <button className={styles.ctaBtn} onClick={onSaveTeam}>
            Set Baseline
          </button>
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
            onPrepareDrag={onPrepareDrag}
            onClearDrag={onClearDrag}
            onSavePlayer={onAddFromSearch}
          />
        )}

        {mode === "recommendations" && (
          <RecommendationsSection
            players={recommendedPlayers}
            savedPlayerIds={savedPlayerIds}
            savingPlayerIds={savingPlayerIds}
            allowAddSaved
            addLabel="Save to Team"
            onSavePlayer={(player) => onAddFromRecommendation(player)}
          />
        )}

        {mode === "idle" && (
          <div className={styles.displayPanel}>
            <div className={styles.placeholder}>
              Use the search bar or click “Get Recommendations!” to see players.
            </div>
          </div>
        )}
      </div>

      {/* Right column */}
      <div className={styles.rightCol}>
        <SavedPlayersSection
          players={savedPlayers}
          assignedIds={assignedIds}
          draggingId={draggingId}
          savingPlayerIds={savingPlayerIds}
          deletingPlayerIds={deletingPlayerIds}
          activePosition={activePosition}
          onPrepareDrag={onPrepareDrag}
          onClearDrag={onClearDrag}
          onAddPlayer={() => {}} // No-op since we don't assign positions
          onDeletePlayer={onDeletePlayer}
        />

        <RecommendationsRadarCard
          statKeys={STAT_KEYS}
          baselineWeakness={baselineWeakness}
          currentWeakness={currentWeakness}
          highlightOrder={highlightOrder}
          loading={weaknessLoading}
          error={weaknessError}
        />
      </div>
    </div>
  );
}
