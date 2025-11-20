import { ProtectedRoute, PageCard } from "@/components";
import { useRecommendations } from "@/features/recommendations/useRecommendations";
import { RecommendationsView } from "@/features/recommendations/RecommendationsView";

export default function RecommendationsPage() {
  const vm = useRecommendations();

  return (
    <ProtectedRoute requireAuth>
      <PageCard title="Recommendations">
        <RecommendationsView {...vm} />
      </PageCard>
    </ProtectedRoute>
  );
}
