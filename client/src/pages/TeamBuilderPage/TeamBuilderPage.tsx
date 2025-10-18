import styles from "./TeamBuilderPage.module.css";

export default function TeamBuilderPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>Team Builder</h1>
      <p className={styles.description}>
        Assemble your ideal roster by blending scouting intel with performance analytics.
        This area will soon let you drag-and-drop players, compare projections, and craft
        the perfect lineup.
      </p>
    </div>
  );
}
