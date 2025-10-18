import styles from "./TeamAnalysisPage.module.css";

export default function TeamAnalysisPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>Team Analysis</h1>
      <p className={styles.description}>
        Deep dives into lineup strengths, weaknesses, and matchup readiness will live here.
        Expect radar charts, trend indicators, and scouting notes tailored to your roster.
      </p>
    </div>
  );
}
