import type { PanelMode } from "./useRecommendations";
import type { TeamWeaknessResponse, SavedPlayer } from "@/api/players";
import type { DiamondPosition, LineupState } from "@/components/TeamBuilder/constants";
import type { DragEvent } from "react";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { RecommendationsSection } from "@/components/TeamBuilder/RecommendationsSection/RecommendationsSection";
import PercentileRadar from "@/components/Radar/PercentileRadar";
import { DiamondPanel } from "@/components/TeamBuilder/DiamondPanel/DiamondPanel";
import styles from "./RecommendationsView.module.css";

type Props = {
  mode: PanelMode;
  query: string;
  lineup: LineupState;
  activePosition: DiamondPosition;
  dropTarget: DiamondPosition | null;
  searchResults: SavedPlayer[];
  searchLoading: boolean;
  searchError: string | null;
  recommendedPlayers: SavedPlayer[];
  recommendationLoading: boolean;
  recommendationError: string | null;
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  weaknessLoading: boolean;
  weaknessError: string | null;
  onGetRecommendations: () => void;
  onSearchChange: (value: string) => void;
  onAddFromSearch: (player: SavedPlayer) => void;
  onAddFromRecommendation: (player: SavedPlayer) => void;
  onSelectPosition: (pos: DiamondPosition) => void;
  onDragOverPosition: (pos: DiamondPosition) => void;
  onDragLeavePosition: () => void;
  onDropOnPosition: (e: DragEvent<HTMLButtonElement>, pos: DiamondPosition) => void;
  onPrepareDrag: (player: SavedPlayer, fromPosition?: DiamondPosition) => void;
  onClearDrag: () => void;
  onClearSlot: (pos: DiamondPosition) => void;
  onSaveLineup: () => void;
  savingLineup: boolean;
  playerOperationError: string | null;
};

const STAT_KEYS: { key: keyof TeamWeaknessResponse; label: string }[] = [
  { key: "strikeout_rate", label: "Strikeout Rate" },
  { key: "walk_rate", label: "Walk Rate" },
  { key: "isolated_power", label: "Iso Power" },
  { key: "on_base_percentage", label: "On Base %" },
  { key: "base_running", label: "Base Running" },
];

// Value (z-score) scale from TeamAnalysis
const MIN_VALUE = -3;
const MAX_VALUE = 2;
const VALUE_SPAN = MAX_VALUE - MIN_VALUE;

const valueToFraction = (value: number) => {
  if (!Number.isFinite(value)) return 0.5;
  const fraction = (value - MIN_VALUE) / VALUE_SPAN;
  return Math.min(Math.max(fraction, 0), 1);
};

const formatValueNumber = (value: number) => {
  if (!Number.isFinite(value)) return "-";
  return (value >= 0 ? "+" : "") + value.toFixed(2).replace(/\.00$/, "");
};

export function RecommendationsView({
  mode,
  query,
  activePosition,
  dropTarget,
  lineup,
  searchResults,
  searchLoading,
  searchError,
  recommendedPlayers,
  recommendationLoading,
  recommendationError,
  baselineWeakness,
  currentWeakness,
  weaknessLoading,
  weaknessError,
  onGetRecommendations,
  onSearchChange,
  onAddFromSearch,
  onAddFromRecommendation,
  onSelectPosition,
  onDragOverPosition,
  onDragLeavePosition,
  onDropOnPosition,
  onPrepareDrag,
  onClearDrag,
  onClearSlot,
  onSaveLineup,
  savingLineup,
  playerOperationError,
}: Props) {
  const toFractions = (weakness: TeamWeaknessResponse | null) =>
    weakness ? STAT_KEYS.map(({ key }) => valueToFraction(weakness[key])) : [];

  const baselineFractions = toFractions(baselineWeakness);
  const currentFractions = toFractions(currentWeakness);

  let highlightOrder: number[] = [];
  if (baselineWeakness && currentWeakness) {
    // Highlight the biggest drops vs. baseline (most negative deltas = got worse)
    highlightOrder = STAT_KEYS.map(({ key }, idx) => ({
      delta: currentWeakness[key] - baselineWeakness[key],
      idx
    }))
      .sort((a, b) => a.delta - b.delta)
      .map((entry) => entry.idx)
      .slice(0, 2);
  } else if (currentWeakness) {
    // Fallback: highlight lowest absolute scores
    highlightOrder = STAT_KEYS.map(({ key }, idx) => ({ value: currentWeakness[key], idx }))
      .sort((a, b) => a.value - b.value)
      .map((entry) => entry.idx)
      .slice(0, 2);
  }

  const ringValues = [-3, -2, -1, 0, 1, 2];
  const ringFractions = ringValues.map(valueToFraction);
  const ringLabels = ringValues.map((v) => (v >= 0 ? `+${v.toFixed(0)}` : v.toFixed(0)));

  return (
    <div className={styles.layout}>
      {/* Left column */}
      <div className={styles.leftCol}>
        {/* Before/After deltas */}
        <div className={styles.weaknessCard}>
          <div className={styles.weaknessTitle}>Changes in Team Weakness</div>
          {weaknessLoading && <div className={styles.placeholder}>Calculating…</div>}
          {weaknessError && <div className={styles.recommendError}>{weaknessError}</div>}
          {!weaknessLoading && !weaknessError && baselineWeakness && currentWeakness ? (
            <div className={styles.weaknessGrid}>
              {STAT_KEYS.slice(0, 3).map(({ key, label }) => {
                const delta = currentWeakness[key] - baselineWeakness[key];
                const cls = delta >= 0 ? styles.weakScoreGreen : styles.weakScoreRed;
                return (
                  <div key={label}>
                    <div className={styles.weakLabel}>{label}</div>
                    <div className={cls}>{delta >= 0 ? "+" : ""}{formatValueNumber(delta)}</div>
                  </div>
                );
              })}
              {STAT_KEYS.slice(3).map(({ key, label }) => {
                const delta = currentWeakness[key] - baselineWeakness[key];
                const cls = delta >= 0 ? styles.weakScoreGreen : styles.weakScoreRed;
                return (
                  <div key={label}>
                    <div className={styles.weakLabel}>{label}</div>
                    <div className={cls}>{delta >= 0 ? "+" : ""}{formatValueNumber(delta)}</div>
                  </div>
                );
              })}
            </div>
          ) : (
            !weaknessLoading &&
            !weaknessError && <div className={styles.placeholder}>Add players to see changes.</div>
          )}
        </div>

        {/* Get Recommendations button */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>Click to get recommendations</div>
          <button
            className={styles.ctaBtn}
            onClick={onGetRecommendations}
            disabled={recommendationLoading}
          >
            {recommendationLoading ? "Loading..." : "Get Recommendations!"}
          </button>
          {recommendationError && <div className={styles.recommendError}>{recommendationError}</div>}
        </div>

        {/* Search bar */}
        <div className={styles.searchCard}>
          <SearchBar
            searchTerm={query}
            onSearchTermChange={onSearchChange}
            statusText={
              query.trim()
                ? searchLoading
                  ? "Searching..."
                  : `${searchResults.length} results`
                : ""
            }
            errorMessage={searchError || undefined}
          />
        </div>

        {/* Results / Recommendations */}
        {mode === "search" && (
          <SearchResultsSection
            players={searchResults}
            onSavePlayer={onAddFromSearch}
            allowAddSaved
            addLabel={`Add to ${activePosition}`}
          />
        )}

        {mode === "recommendations" && (
          <RecommendationsSection
            players={recommendedPlayers}
            onSavePlayer={onAddFromRecommendation}
            allowAddSaved
            addLabel={`Add to ${activePosition}`}
          />
        )}

        {mode === "idle" && (
          <div className={styles.displayPanel}>
            <div className={styles.placeholder}>
              Search or click “Get Recommendations!” to see players.
            </div>
          </div>
        )}
      </div>

      {/* Right column */}
      <div className={styles.rightCol}>
        {/* Radar */}
        <div className={styles.radarCard}>
          <div className={styles.radarHeader}>Before/After</div>
          <div className={styles.radarSubheader}>Weakness radar</div>
          {weaknessLoading && <div className={styles.radarPlaceholder}>Calculating…</div>}
          {weaknessError && <div className={styles.radarPlaceholder}>{weaknessError}</div>}
          {!weaknessLoading && !weaknessError && currentFractions.length > 0 ? (
            <PercentileRadar
              axes={STAT_KEYS.map(({ label }) => ({ label }))}
              teamPercentiles={currentFractions}
              leaguePercentiles={baselineFractions.length ? baselineFractions : undefined}
              highlightOrder={highlightOrder}
              ringFractions={ringFractions}
              ringLabels={ringLabels}
              showBaselineRing={false}
              legendItems={[
                "Blue = current lineup",
                baselineFractions.length ? "Orange = baseline lineup" : "Orange baseline unavailable",
                "0 baseline = league average; positive = above average (stronger)"
              ]}
            />
          ) : (
            !weaknessLoading &&
            !weaknessError && <div className={styles.radarPlaceholder}>Add players to view radar.</div>
          )}
        </div>

        {/* Lineup placeholder */}
        <div className={styles.diamondCard}>
          <div className={styles.diamondHeader}>
            <div>Your lineup</div>
            <div className={styles.activeBadge}>ACTIVE: {activePosition}</div>
          </div>
          <div className={styles.diamondCanvas}>
            <DiamondPanel
              lineup={lineup}
              activePosition={activePosition}
              dropTarget={dropTarget}
              dragPlayer={null}
              onSelectPosition={onSelectPosition}
              onDragOverPosition={onDragOverPosition}
              onDragLeavePosition={onDragLeavePosition}
              onDropOnPosition={onDropOnPosition}
              onPrepareDrag={onPrepareDrag}
              onClearDragState={onClearDrag}
              onClearSlot={onClearSlot}
            />
          </div>
          <div className={styles.diamondFooter}>
            {playerOperationError && (
              <div className={styles.recommendError}>{playerOperationError}</div>
            )}
            <button className={styles.saveBtn} onClick={onSaveLineup} disabled={savingLineup}>
              {savingLineup ? "Saving..." : "Save Lineup"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
