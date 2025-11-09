import { useState } from "react";
import styles from "./TeamAnalysisPage.module.css";
import WeaknessView from "./components/WeaknessView";

// TODO: Replace with real player data. This is placeholder data for UI development.
const STATIC_PLAYERS = [
  { id: 1, name: "Shohei Ohtani", years_active: "LA Dodgers", image_url: "" },
  { id: 2, name: "Mookie Betts", years_active: "LA Dodgers", image_url: "" },
  { id: 3, name: "Freddie Freeman", years_active: "LA Dodgers", image_url: "" },
  { id: 4, name: "Will Smith", years_active: "LA Dodgers", image_url: "" },
  { id: 5, name: "Max Muncy", years_active: "LA Dodgers", image_url: "" },
];

export default function TeamAnalysisPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className={styles.page}>
      {/* Sidebar toggle */}
      <button
        className={`${styles.sidebarHandle} ${sidebarOpen ? styles.handleOpen : styles.handleClosed}`}
        onClick={() => setSidebarOpen(o => !o)}
        aria-label="Toggle team sidebar"
        title={sidebarOpen ? "Hide team sidebar" : "Show team sidebar"}
      >
        {sidebarOpen ? "◀" : "▶"}
      </button>

      {/* Sidebar */}
      <div
        className={`${styles.sidebarContainer} ${
          sidebarOpen ? styles.sidebarContainerOpen : styles.sidebarContainerClosed
        }`}
      >
        <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : styles.sidebarHidden}`}>
          {sidebarOpen && (
            <>
              <div className={styles.sidebarHeader}>
                <div className={styles.teamTitle}>TeamName1</div>
              </div>

              <div className={styles.playerList}>
                {STATIC_PLAYERS.map(p => (
                  <div key={p.id} className={styles.playerCard}>
                    <img
                      src={p.image_url || "https://via.placeholder.com/50"}
                      alt={p.name}
                      className={styles.playerImage}
                    />
                    <div className={styles.playerInfo}>
                      <div className={styles.playerName}>{p.name}</div>
                      <div className={styles.playerTeam}>{p.years_active}</div>
                    </div>
                    <button className={styles.playerMenu} aria-label="Player menu">⋮</button>
                  </div>
                ))}
                <button className={styles.viewAllButton}>View All</button>
              </div>
            </>
          )}
        </aside>
      </div>

      {/* Header (single tab label) */}
      <main className={styles.mainContent}>
        <nav className={styles.tabNav}>
          <div className={`${styles.tab} ${styles.tabActive}`}>Weakness</div>
        </nav>

        <div className={styles.tabContent}>
          <WeaknessView />
        </div>
      </main>
    </div>
  );
}