import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import styles from "./TeamBuilderPage.module.css";

type DiamondPosition = "LF" | "CF" | "RF" | "3B" | "SS" | "2B" | "1B" | "P" | "C" | "DH";

const DEFAULT_PLAYER_IMAGE =
  "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current";

const positionOrder: DiamondPosition[] = ["LF", "CF", "RF", "3B", "SS", "2B", "1B", "P", "C", "DH"];

const positionCoordinates: Record<DiamondPosition, { top: string; left: string }> = {
  LF: { top: "16%", left: "13%" },
  CF: { top: "8%", left: "50%" },
  RF: { top: "16%", left: "87%" },
  SS: { top: "38%", left: "32%" },
  "2B": { top: "38%", left: "68%" },
  "3B": { top: "56%", left: "18%" },
  "1B": { top: "56%", left: "82%" },
  P: { top: "48%", left: "50%" },
  C: { top: "75%", left: "50%" },
  DH: { top: "82%", left: "80%" }
};

type LineupState = Record<DiamondPosition, SavedPlayer | null>;

export default function TeamBuilderPage() {
  const [lineup, setLineup] = useState<LineupState>(() =>
    positionOrder.reduce((acc, position) => ({ ...acc, [position]: null }), {} as LineupState)
  );
  const [activePosition, setActivePosition] = useState<DiamondPosition | null>("CF");
  const [searchTerm, setSearchTerm] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [error, setError] = useState("");
  const searchControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const fetchSaved = async () => {
      const result = await playerActions.getSavedPlayers();
      if (result.success && result.data) {
        setSavedPlayers(result.data);
      }
    };

    void fetchSaved();
  }, []);

  const performSearch = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) {
      searchControllerRef.current?.abort();
      searchControllerRef.current = null;
      setSearchResults([]);
      setIsSearching(false);
      setError("");
      return;
    }

    searchControllerRef.current?.abort();
    const controller = new AbortController();
    searchControllerRef.current = controller;

    setIsSearching(true);
    setError("");
    const result = await playerActions.searchPlayers(trimmed, controller.signal);

    if (searchControllerRef.current !== controller) {
      return;
    }

    setIsSearching(false);

    if (result.success && result.data) {
      setSearchResults(result.data);
      searchControllerRef.current = null;
      return;
    }

    if (result.aborted) {
      searchControllerRef.current = null;
      return;
    }

    setSearchResults([]);
    setError(result.error || "Search failed");
    searchControllerRef.current = null;
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      void performSearch(searchTerm);
    }, 250);

    return () => clearTimeout(timer);
  }, [performSearch, searchTerm]);

  useEffect(() => {
    return () => {
      searchControllerRef.current?.abort();
    };
  }, []);

  const availablePlayers = useMemo(() => {
    if (searchTerm.trim()) {
      return searchResults.map((result) => ({
        id: result.id,
        name: result.name,
        image_url: result.image_url,
        years_active: result.years_active
      }));
    }

    return savedPlayers;
  }, [searchResults, searchTerm, savedPlayers]);

  const handleAssign = (player: SavedPlayer) => {
    const slot = activePosition;
    if (!slot) return;

    setLineup((prev) => ({
      ...prev,
      [slot]: player
    }));
  };

  const handleClearSlot = (position: DiamondPosition) => {
    setLineup((prev) => ({
      ...prev,
      [position]: null
    }));
  };

  const assignedIds = useMemo(
    () =>
      new Set(
        positionOrder
          .map((pos) => lineup[pos]?.id)
          .filter((id): id is number => typeof id === "number")
      ),
    [lineup]
  );

  const allShownAssigned =
    availablePlayers.length > 0 &&
    availablePlayers.every((player) => assignedIds.has(player.id));

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.kicker}>Interactive lineup designer</p>
          <h1 className={styles.title}>Team Builder</h1>
        </div>

        <div className={styles.searchBar}>
          <span className={styles.searchIcon} aria-hidden="true">⌕</span>
          <input
            type="text"
            placeholder="Search players by name..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
          <span className={styles.searchStatus}>
            {isSearching ? "Searching…" : `${availablePlayers.length} players`}
          </span>
        </div>
      </header>

      <section className={styles.builderShell}>
        <div className={styles.diamondPanel}>
          <header className={styles.panelHeader}>
            <h2>Current Lineup</h2>
            <p>Select a position to assign players.</p>
          </header>

          <div className={styles.diamond}>
            <svg className={styles.diamondLines} viewBox="0 0 400 400">
              <path d="M200 40 L360 200 L200 360 L40 200 Z" />
              <path d="M200 110 L290 200 L200 290 L110 200 Z" />
              <circle cx="200" cy="200" r="10" />
            </svg>

            {positionOrder.map((position) => {
              const assigned = lineup[position];
              const isActive = activePosition === position;

              return (
                <div
                  key={position}
                  className={`${styles.positionNode} ${isActive ? styles.active : ""} ${
                    assigned ? styles.filled : ""
                  }`}
                  style={positionCoordinates[position]}
                >
                  <button
                    type="button"
                    className={styles.positionTrigger}
                    onClick={() => setActivePosition(position)}
                    aria-pressed={isActive}
                  >
                    <span className={styles.positionLabel}>{position}</span>
                    {assigned && (
                      <span className={styles.positionPlayer}>
                        <img
                          src={assigned.image_url || DEFAULT_PLAYER_IMAGE}
                          alt={assigned.name}
                          onError={(e) => {
                            e.currentTarget.src = DEFAULT_PLAYER_IMAGE;
                          }}
                        />
                        <span className={styles.positionName}>{assigned.name}</span>
                      </span>
                    )}
                  </button>
                  {assigned && (
                    <button
                      type="button"
                      className={styles.clearSlot}
                      onClick={(event) => {
                        event.stopPropagation();
                        handleClearSlot(position);
                      }}
                      aria-label={`Clear ${position} position`}
                    >
                      ×
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <aside className={styles.availablePanel}>
          <header className={styles.panelHeader}>
            <div>
              <h2>Available Players</h2>
              <p>
                {searchTerm
                  ? "Search results are shown below."
                  : "Using saved players. Add more from the dashboard to expand this list."}
              </p>
            </div>
            <div className={styles.positionHint}>
              {activePosition ? (
                <span>Assigning to <strong>{activePosition}</strong></span>
              ) : (
                <span>Select a position to begin</span>
              )}
            </div>
          </header>

          <div className={styles.playerScroller}>
            {error && <p className={styles.errorMessage}>{error}</p>}

            {availablePlayers.length === 0 && !error && (
              <div className={styles.emptyState}>
                <p>No players to show yet.</p>
                <span>
                  Save players from the dashboard or search above to scout new talent.
                </span>
              </div>
            )}

            {availablePlayers.map((player) => {
              const alreadyAssigned = assignedIds.has(player.id);

              return (
                <div key={player.id} className={styles.playerRow}>
                  <div className={styles.playerProfile}>
                    <img
                      src={player.image_url || DEFAULT_PLAYER_IMAGE}
                      alt={player.name}
                      onError={(e) => {
                        e.currentTarget.src = DEFAULT_PLAYER_IMAGE;
                      }}
                    />
                    <div>
                      <p className={styles.playerName}>{player.name}</p>
                      <span className={styles.playerMeta}>{player.years_active || "No years listed"}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className={styles.addButton}
                    onClick={() => handleAssign(player)}
                    disabled={!activePosition || alreadyAssigned}
                  >
                    {!activePosition
                      ? "Select Position"
                      : alreadyAssigned
                      ? "Assigned"
                      : `Add to ${activePosition}`}
                  </button>
                </div>
              );
            })}

            {allShownAssigned && !error && (
              <div className={styles.assignmentMessage}>
                All listed players are already assigned. Add more prospects from the dashboard to
                keep building your lineup.
              </div>
            )}
          </div>
        </aside>
      </section>
    </div>
  );
}
