import { ProtectedRoute } from "@/components";
import { useRecommendations } from "@/features/recommendations/useRecommendations.ts";
import { RecommendationsView } from "@/features/recommendations/RecommendationsView.tsx";
import styles from "./RecommendationsPage.module.css";

export default function RecommendationsPage() {
  const vm = useRecommendations();

  return (
    <ProtectedRoute requireAuth>
      <div className={styles.page}>
        <RecommendationsView
          mode={vm.mode}
          query={vm.query}
          activePosition={vm.activePosition}
          dropTarget={vm.dropTarget}
          lineup={vm.lineup}
          searchResults={vm.searchResults}
          searchLoading={vm.searchLoading}
          searchError={vm.searchError}
          recommendedPlayers={vm.recommendedPlayers}
          recommendationLoading={vm.recommendationLoading}
          recommendationError={vm.recommendationError}
          baselineWeakness={vm.baselineWeakness}
          currentWeakness={vm.currentWeakness}
          weaknessLoading={vm.weaknessLoading}
          weaknessError={vm.weaknessError}
          onGetRecommendations={vm.onGetRecommendations}
          onSearchChange={vm.onSearchChange}
          onAddFromSearch={vm.onAddFromSearch}
          onAddFromRecommendation={vm.onAddFromRecommendation}
          onSelectPosition={vm.setActivePosition}
          onDragOverPosition={vm.setDropTarget}
          onDragLeavePosition={() => vm.setDropTarget(null)}
          onDropOnPosition={vm.onPositionDrop}
          onPrepareDrag={vm.onPrepareDrag}
          onClearDrag={vm.onClearDrag}
          onClearSlot={vm.onClearSlot}
          onSaveLineup={vm.onSaveLineup}
          savingLineup={vm.savingLineup}
          playerOperationError={vm.playerOperationError}
        />
      </div>
    </ProtectedRoute>
  );
}
