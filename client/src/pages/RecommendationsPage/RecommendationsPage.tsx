import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { ProtectedRoute, PageCard } from "@/components";
import { ROUTES } from "@/config";
import { useRecommendations } from "./components/useRecommendations";
import { RecommendationsView } from "./components/RecommendationsView";
import styles from "./RecommendationsPage.module.css";

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
