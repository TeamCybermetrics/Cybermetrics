import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { ProtectedRoute, PageCard } from "@/components";
import { ROUTES } from "@/config";
import { useRecommendations } from "./components/useRecommendations";
import { RecommendationsView } from "./components/RecommendationsView";
import styles from "./RecommendationsPage.module.css";

/**
 * Page component that displays recommendations inside a protected card layout with a back navigation to the Lineup Constructor.
 *
 * @returns A React element containing a ProtectedRoute-wrapped PageCard titled "Roster Constructor" with a header action linking to the Lineup Constructor and the RecommendationsView rendered with the recommendations view model.
 */
export default function RecommendationsPage() {
  const vm = useRecommendations();

  return (
    <ProtectedRoute requireAuth>
      <PageCard 
        title="Roster Constructor"
        headerAction={
          <Link to={ROUTES.LINEUP_CONSTRUCTOR} className={styles.navButton}>
            <ArrowLeft size={16} /> Lineup Constructor
          </Link>
        }
      >
        <RecommendationsView {...vm} />
      </PageCard>
    </ProtectedRoute>
  );
}