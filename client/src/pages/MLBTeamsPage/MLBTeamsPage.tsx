import styles from "./MLBTeamsPage.module.css";

export default function MLBTeamsPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>MLB Teams</h1>
      <p className={styles.description}>
        League-wide scouting reports, organizational depth charts, and opponent scouting
        packs will be available here to help you prep for every series.
      </p>
    </div>
  );
}
