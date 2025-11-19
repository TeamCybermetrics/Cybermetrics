import { ProtectedRoute } from "@/components";
import { useRecommendations } from "@/features/recommendations/useRecommendations.ts";
import { RecommendationsView } from "@/features/recommendations/RecommendationsView.tsx";
import styles from "./RecommendationsPage.module.css";

export default function RecommendationsPage() {
  const vm = useRecommendations();
  const { mode, searchTerm, onGetRecommendations, setSearchTerm, onSaveTeam } = vm;

  return (
    <ProtectedRoute requireAuth>
      <div className={styles.page}>
        <RecommendationsView
          mode={mode}
          query={searchTerm}
          onGetRecommendations={onGetRecommendations}
          onSearchChange={setSearchTerm}
          onSaveLineup={onSaveTeam}
        />
      </div>
    </ProtectedRoute>
  );
}