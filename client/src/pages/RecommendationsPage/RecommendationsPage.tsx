import styles from "./RecommendationsPage.module.css";

export default function RecommendationsPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>Recommendations</h1>
      <p className={styles.description}>
        Personalized acquisition targets, lineup tweaks, and player development plans will
        surface here based on your saved roster and scouting filters.
      </p>
    </div>
  );
}
