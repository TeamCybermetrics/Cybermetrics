import type { DragEvent } from "react";
import type { SavedPlayer } from "@/api/players";
import type { DiamondPosition, LineupState } from "@/components/TeamBuilder/constants";
import type { PanelMode } from "./useRecommendations";
import { SearchBar } from "@/components/TeamBuilder/SearchBar/SearchBar";
import { SearchResultsSection } from "@/components/TeamBuilder/SearchResultsSection/SearchResultsSection";
import { RecommendationsSection } from "@/components/TeamBuilder/RecommendationsSection/RecommendationsSection";
import { DiamondPanel } from "@/components/TeamBuilder/DiamondPanel/DiamondPanel";
import styles from "./RecommendationsView.module.css";

type Props = {
  // Panel
  mode: PanelMode;
  searchTerm: string;
  
  // Lineup
  lineup: LineupState;
  activePosition: DiamondPosition | null;
  dropTarget: DiamondPosition | null;
  draggingId: number | null;
  
  // Players
  savedPlayers: SavedPlayer[];
  searchResultPlayers: SavedPlayer[];
  recommendedPlayers: any[];
  
  // Sets
  savedPlayerIds: Set<number>;
  assignedIds: Set<number>;
  savingPlayerIds: Set<number>;
  
  // Status
  hasSearchTerm: boolean;
  isRecommending: boolean;
  recommendationError: string;
  playerOperationError: string;
  
  // Handlers
  setSearchTerm: (value: string) => void;
  setActivePosition: (pos: DiamondPosition) => void;
  setDropTarget: (pos: DiamondPosition | null) => void;
  handleSavePlayerOnly: (player: SavedPlayer) => void;
  handleClearSlot: (pos: DiamondPosition) => void;
  prepareDragPlayer: (player: SavedPlayer, fromPosition?: DiamondPosition) => void;
  clearDragState: () => void;
  handlePositionDrop: (e: DragEvent<HTMLButtonElement>, pos: DiamondPosition) => void;
  saveTeam: () => void;
  handleGetRecommendations: () => void;
};

export function RecommendationsView({
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
  hasSearchTerm,
  isRecommending,
  recommendationError,
  playerOperationError,
  setSearchTerm,
  setActivePosition,
  setDropTarget,
  handleSavePlayerOnly,
  handleClearSlot,
  prepareDragPlayer,
  clearDragState,
  handlePositionDrop,
  saveTeam,
  handleGetRecommendations,
}: Props) {
  return (
    <div className={styles.layout}>
      {/* LEFT COLUMN */}
      <div className={styles.leftCol}>
        {/* Team Weakness Card */}
        <div className={styles.weaknessCard}>
          <div className={styles.weaknessTitle}>Changes in Team Weakness</div>
          <div className={styles.weaknessGrid}>
            <div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
            </div>
            <div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
            </div>
          </div>
        </div>

        {/* Get Recommendations Button */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>Click to get recommendations</div>
          <button
            className={styles.ctaBtn}
            onClick={handleGetRecommendations}
            disabled={isRecommending}
          >
            {isRecommending ? "Loading..." : "Get Recommendations!"}
          </button>
          {recommendationError && (
            <div className={styles.recommendError}>{recommendationError}</div>
          )}
        </div>

        {/* Search Bar */}
        <div className={styles.searchCard}>
          <SearchBar
            searchTerm={searchTerm}
            onSearchTermChange={setSearchTerm}
            statusText={
              hasSearchTerm
                ? `${searchResultPlayers.length} results`
                : ""
            }
            errorMessage={playerOperationError}
          />
        </div>

        {/* Unified Output Panel */}
        {mode === "search" && (
          <SearchResultsSection
            players={searchResultPlayers}
            savedPlayerIds={savedPlayerIds}
            assignedIds={assignedIds}
            draggingId={draggingId}
            savingPlayerIds={savingPlayerIds}
            onPrepareDrag={prepareDragPlayer}
            onClearDrag={clearDragState}
            onSavePlayer={handleSavePlayerOnly}
          />
        )}

        {mode === "recommendations" && (
          <RecommendationsSection
            players={recommendedPlayers}
            savedPlayerIds={savedPlayerIds}
            savingPlayerIds={savingPlayerIds}
            onSavePlayer={handleSavePlayerOnly}
          />
        )}

        {mode === "idle" && (
          <div className={styles.displayPanel}>
            <div className={styles.placeholder}>
              Use the search bar or click "Get Recommendations!" to see results here.
            </div>
          </div>
        )}
      </div>

      {/* RIGHT COLUMN */}
      <div className={styles.rightCol}>
        {/* Radar Card */}
        <div className={styles.radarCard}>
          <div className={styles.radarHeader}>Before/After</div>
          <div className={styles.radarSubheader}>Weakness radar</div>
          <div className={styles.radarPlaceholder} />
        </div>

        {/* Diamond Panel */}
        <div className={styles.diamondCard}>
          <div className={styles.diamondHeader}>
            <div>Your lineup</div>
            {activePosition && (
              <div className={styles.activeBadge}>ACTIVE: {activePosition}</div>
            )}
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
              onDropOnPosition={handlePositionDrop}
              onPrepareDrag={prepareDragPlayer}
              onClearDragState={clearDragState}
              onClearSlot={handleClearSlot}
              onSaveTeam={saveTeam}
            />
          </div>
        </div>
      </div>
    </div>
  );
}