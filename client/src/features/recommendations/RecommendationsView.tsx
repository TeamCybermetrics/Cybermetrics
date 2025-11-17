import type { PanelMode } from "./useRecommendations";
import type { TeamWeaknessResponse, SavedPlayer } from "@/api/players";
import type { DiamondPosition, LineupState } from "@/components/TeamBuilder/constants";
import type { DragEvent } from "react";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { RecommendationsSection } from "@/components/TeamBuilder/RecommendationsSection/RecommendationsSection";
import PercentileRadar from "@/components/Radar/PercentileRadar";
import { DiamondPanel } from "@/components/TeamBuilder/DiamondPanel/DiamondPanel";
import {
  formatZScore,
  RING_FRACTIONS,
  RING_LABELS,
  valueToFraction,
  Z_SCORE_CONFIG
} from "@/utils/zScoreRadar";
import styles from "./RecommendationsView.module.css";

type Props = {
  mode: PanelMode;
  searchTerm: string;
  lineup: LineupState;
  activePosition: DiamondPosition;
  dropTarget: DiamondPosition | null;
  draggingId: number | null;
  searchResults: SavedPlayer[];
  recommendedPlayers: SavedPlayer[];
  savedPlayerIds: Set<number>;
  assignedIds: Set<number>;
  savingPlayerIds: Set<number>;
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
  setDropTarget: (pos: DiamondPosition | null) => void;
  onClearSlot: (pos: DiamondPosition) => void;
  onPrepareDrag: (player: SavedPlayer, fromPosition?: DiamondPosition) => void;
  onClearDrag: () => void;
  onPositionDrop: (e: DragEvent<HTMLButtonElement>, pos: DiamondPosition) => void;
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

const RADAR_RADIUS = Z_SCORE_CONFIG.RADAR_RADIUS; // keep labels centered

const formatValueNumber = (value: number) => formatZScore(value, 2);

export function RecommendationsView({
  mode,
  searchTerm,
  lineup,
  activePosition,
  dropTarget,
  draggingId,
  searchResults,
  recommendedPlayers,
  savedPlayerIds,
  assignedIds,
  savingPlayerIds,
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
  setDropTarget,
  onClearSlot,
  onPrepareDrag,
  onClearDrag,
  onPositionDrop,
  onSaveTeam,
  onGetRecommendations,
  onAddFromSearch,
  onAddFromRecommendation,
}: Props) {
  const toFractions = (weakness: TeamWeaknessResponse | null) =>
    weakness ? STAT_KEYS.map(({ key }) => valueToFraction(weakness[key])) : [];

  const baselineFractions = toFractions(baselineWeakness);
  const currentFractions = toFractions(currentWeakness);

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
        <div className={styles.weaknessCard}>
          <div className={styles.weaknessTitle}>Changes in Team Weakness</div>
          {weaknessLoading && <div className={styles.placeholder}>Calculating…</div>}
          {weaknessError && <div className={styles.recommendError}>{weaknessError}</div>}
          {!weaknessLoading && !weaknessError && baselineWeakness && currentWeakness ? (
            <div className={styles.weaknessGrid}>
              {STAT_KEYS.map(({ key, label }) => {
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
            !weaknessLoading && !weaknessError && <div className={styles.placeholder}>Add players to see changes.</div>
          )}
        </div>

        {/* Get Recommendations button */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>Click to get recommendations</div>
          <button className={styles.ctaBtn} onClick={onGetRecommendations} disabled={isRecommending}>
            {isRecommending ? "Loading..." : "Get Recommendations!"}
          </button>
          {recommendationError && <div className={styles.recommendError}>{recommendationError}</div>}
        </div>

        {/* Search bar */}
        <div className={styles.searchCard}>
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
        </div>

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
            addLabel={`Add to ${activePosition}`}
            onSavePlayer={onAddFromRecommendation}
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
              ringFractions={RING_FRACTIONS}
              ringLabels={RING_LABELS}
              baselinePercentile={0.5}
              showBaselineRing
              ringLabelOffsetY={RADAR_RADIUS * 0.5}
              legendItems={[
                "Blue = current lineup",
                baselineFractions.length ? "Orange = baseline lineup" : "Orange baseline unavailable",
                "0 = league average; positive = above average (stronger)"
              ]}
            />
          ) : (
            !weaknessLoading &&
            !weaknessError && <div className={styles.radarPlaceholder}>Add players to view radar.</div>
          )}
        </div>

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
              onSelectPosition={setActivePosition}
              onDragOverPosition={setDropTarget}
              onDragLeavePosition={() => setDropTarget(null)}
              onDropOnPosition={onPositionDrop}
              onPrepareDrag={onPrepareDrag}
              onClearDragState={onClearDrag}
              onClearSlot={onClearSlot}
            />
          </div>
          <div className={styles.diamondFooter}>
            <button className={styles.saveBtn} onClick={onSaveTeam}>
              Save Lineup as baseline
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
