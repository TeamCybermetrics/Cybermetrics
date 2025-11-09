import { useEffect, useState } from "react";
import styles from "./TeamAnalysisPage.module.css";
import WeaknessView from "./components/WeaknessView";
import { playerActions } from "@/actions/players";
import type { SavedPlayer } from "./types";

export default function TeamAnalysisPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true);
  const [playersError, setPlayersError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      setLoadingPlayers(true);
      setPlayersError(null);
      const result = await playerActions.getSavedPlayers();
      if (!isMounted) return;
      if (result.success) {
        setSavedPlayers(result.data || []);
      } else {
        setPlayersError(result.error || "Failed to load players");
      }
      setLoadingPlayers(false);
    };

    load();
    return () => {
      isMounted = false;
    };
  }, []);

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
                <div className={styles.teamTitle}>Your Team</div>
              </div>

              <div className={styles.playerList}>
                {loadingPlayers && (
                  <div className={styles.loadingState}>Loading saved players…</div>
                )}
                {!loadingPlayers && playersError && (
                  <div className={styles.errorState}>
                    <span>{playersError}</span>
                    <button
                      className={styles.retryButton}
                      onClick={() => {
                        setLoadingPlayers(true);
                        playerActions.getSavedPlayers().then(res => {
                          if (res.success) {
                            setSavedPlayers(res.data || []);
                            setPlayersError(null);
                          } else {
                            setPlayersError(res.error || "Failed to load players");
                          }
                          setLoadingPlayers(false);
                        });
                      }}
                    >Retry</button>
                  </div>
                )}
                {!loadingPlayers && !playersError && savedPlayers.length === 0 && (
                  <div className={styles.emptyState}>No saved players yet.</div>
                )}
                {!loadingPlayers && !playersError && savedPlayers.map(p => (
                  <div key={p.id} className={styles.playerCard}>
                    <img
                      src={p.image_url || "https://via.placeholder.com/50"}
                      alt={p.name}
                      className={styles.playerImage}
                    />
                    <div className={styles.playerInfo}>
                      <div className={styles.playerName}>{p.name}</div>
                      <div className={styles.playerTeam}>{p.years_active || ""}</div>
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