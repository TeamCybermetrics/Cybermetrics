import { useState } from "react";
import styles from "./TeamAnalysisPage.module.css";
import StrengthView from "./components/StrengthView";
import WeaknessView from "./components/WeaknessView";

type Tab = "strength" | "weakness";

const STATIC_PLAYERS = [
  { id: 1, name: "Shohei Ohtani", years_active: "LA Dodgers", image_url: "" },
  { id: 2, name: "Mookie Betts", years_active: "LA Dodgers", image_url: "" },
  { id: 3, name: "Freddie Freeman", years_active: "LA Dodgers", image_url: "" },
  { id: 4, name: "Shohei Ohtani", years_active: "LA Dodgers", image_url: "" },
  { id: 5, name: "Shohei Ohtani", years_active: "LA Dodgers", image_url: "" },
];

export default function TeamAnalysisPage() {
  const [activeTab, setActiveTab] = useState<Tab>("strength");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className={styles.page}>
      {/* Floating handle (always visible) */}
      <button
        className={`${styles.sidebarHandle} ${sidebarOpen ? styles.handleOpen : styles.handleClosed}`}
        onClick={() => setSidebarOpen(o => !o)}
        aria-label="Toggle team sidebar"
        title={sidebarOpen ? "Hide team sidebar" : "Show team sidebar"}
      >
        {sidebarOpen ? "◀" : "▶"}
      </button>

      {/* Sidebar container (width collapses to 0) */}
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

      <main className={styles.mainContent}>
        <nav className={styles.tabNav}>
          <button
            className={`${styles.tab} ${activeTab === "strength" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("strength")}
          >
            Strength
          </button>
          <button
            className={`${styles.tab} ${activeTab === "weakness" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("weakness")}
          >
            Weakness
          </button>
        </nav>

        <div className={styles.tabContent}>
          {activeTab === "strength" && <StrengthView />}
          {activeTab === "weakness" && <WeaknessView />}
        </div>
      </main>
    </div>
  );
}