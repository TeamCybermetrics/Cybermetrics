import { ProtectedRoute } from "@/components";
import { useRecommendations } from "@/features/recommendations/useRecommendations.ts";
import { RecommendationsView } from "@/features/recommendations/RecommendationsView.tsx";
import styles from "./RecommendationsPage.module.css";

export default function RecommendationsPage() {
  const vm = useRecommendations();

  return (
    <ProtectedRoute requireAuth>
      <div className={styles.page}>
        <RecommendationsView {...vm} />
      </div>
    </ProtectedRoute>
  );
}
