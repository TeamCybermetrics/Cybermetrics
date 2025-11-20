import { ProtectedRoute, PageCard } from "@/components";
import { useRecommendations } from "./components/useRecommendations";
import { RecommendationsView } from "./components/RecommendationsView";

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
