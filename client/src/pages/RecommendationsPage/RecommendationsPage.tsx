import { ProtectedRoute } from "@/components";
import styles from "./RecommendationsPage.module.css";

export default function RecommendationsPage() {
  return (
    <ProtectedRoute requireAuth>
      <div className={styles.page}>
        <header className={styles.header}>
          <h1 className={styles.title}>Recommendations</h1>
          <p className={styles.subtitle}>Coming soon</p>
        </header>

        <div className={styles.content}>
          {/* blank for now */}
        </div>
      </div>
    </ProtectedRoute>
  );
}