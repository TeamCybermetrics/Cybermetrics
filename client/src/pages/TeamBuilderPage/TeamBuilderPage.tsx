import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent, ChangeEvent } from "react";
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
  const dragPlayerRef = useRef<SavedPlayer | null>(null);
  const [dropTarget, setDropTarget] = useState<DiamondPosition | null>(null);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [importError, setImportError] = useState("");
  const [importSummary, setImportSummary] = useState<{ imported: number; skipped: number; total: number } | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadSavedPlayers = useCallback(async () => {
    const result = await playerActions.getSavedPlayers();
    if (result.success && result.data) {
      setSavedPlayers(result.data);
    } else if (!result.success) {
      setError(result.error || "Failed to load saved players");
    }
  }, []);

  useEffect(() => {
    void loadSavedPlayers();
  }, [loadSavedPlayers]);

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
      })) as SavedPlayer[];
    }

    return savedPlayers;
  }, [searchResults, searchTerm, savedPlayers]);

  const assignPlayerToPosition = useCallback((player: SavedPlayer, position: DiamondPosition) => {
    setLineup((prev) => {
      const next: LineupState = { ...prev };

      positionOrder.forEach((slot) => {
        if (next[slot]?.id === player.id) {
          next[slot] = null;
        }
      });

      next[position] = player;
      return next;
    });

    setActivePosition(position);
  }, []);

  const handleAssign = (player: SavedPlayer) => {
    const slot = activePosition;
    if (!slot) return;
    assignPlayerToPosition(player, slot);
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

  const prepareDragPlayer = (player: SavedPlayer, fromPosition?: DiamondPosition) => {
    dragPlayerRef.current = { ...player };
    setDraggingId(player.id);
    if (fromPosition) {
      setActivePosition(fromPosition);
    }
  };

  const clearDragState = () => {
    dragPlayerRef.current = null;
    setDropTarget(null);
    setDraggingId(null);
  };

  const handlePositionDrop = (event: DragEvent<HTMLDivElement>, position: DiamondPosition) => {
    event.preventDefault();
    event.stopPropagation();
    const player = dragPlayerRef.current;
    if (!player) {
      clearDragState();
      return;
    }

    assignPlayerToPosition(player, position);
    clearDragState();
  };

  const handleImportClick = () => {
    if (!isImporting) {
      fileInputRef.current?.click();
    }
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setIsImporting(true);
    setImportError("");
    setImportSummary(null);

    const result = await playerActions.importSavedPlayers(file);

    if (result.success && result.data) {
      const { imported, total_rows, skipped } = result.data;
      setImportSummary({ imported, total: total_rows, skipped: skipped.length });
      await loadSavedPlayers();
    } else {
      setImportError(result.error || "Failed to import players");
    }

    setIsImporting(false);
    event.target.value = "";
  };

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
              const isDropTarget = dropTarget === position && dragPlayerRef.current;

              return (
                <div
                  key={position}
                  className={`${styles.positionNode} ${isActive ? styles.active : ""} ${
                    assigned ? styles.filled : ""
                  } ${isDropTarget ? styles.droppable : ""}`}
                  style={positionCoordinates[position]}
                  onDragOver={(event) => {
                    event.preventDefault();
                    if (dragPlayerRef.current) {
                      setDropTarget(position);
                    }
                  }}
                  onDragLeave={(event) => {
                    event.preventDefault();
                    if (dropTarget === position) {
                      setDropTarget(null);
                    }
                  }}
                  onDrop={(event) => handlePositionDrop(event, position)}
                >
                  <button
                    type="button"
                    className={styles.positionTrigger}
                    onClick={() => setActivePosition(position)}
                    aria-pressed={isActive}
                    draggable={Boolean(assigned)}
                    onDragStart={(event) => {
                      if (assigned) {
                        event.dataTransfer.setData("text/plain", String(assigned.id));
                        event.dataTransfer.effectAllowed = "move";
                        prepareDragPlayer(assigned, position);
                      }
                    }}
                    onDragEnd={() => {
                      clearDragState();
                    }}
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
                  : "Using saved players. Add more from the dashboard or import your own CSV."}
              </p>
            </div>
            <div className={styles.panelActions}>
              <div className={styles.positionHint}>
                {activePosition ? (
                  <span>Assigning to <strong>{activePosition}</strong></span>
                ) : (
                  <span>Select a position to begin</span>
                )}
              </div>
              <div className={styles.importControls}>
                <button
                  type="button"
                  className={styles.importButton}
                  onClick={handleImportClick}
                  disabled={isImporting}
                >
                  {isImporting ? "Importing…" : "Import CSV"}
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  className={styles.importInput}
                  onChange={handleFileChange}
                  aria-label="Upload CSV of players"
                />
              </div>
            </div>
          </header>

          {(importSummary || importError) && (
            <div className={styles.importFeedback}>
              {importSummary && (
                <span>
                  Imported <strong>{importSummary.imported}</strong> of {importSummary.total} rows
                  {importSummary.skipped > 0 && ` • ${importSummary.skipped} skipped`}
                </span>
              )}
              {importError && <span className={styles.importError}>{importError}</span>}
            </div>
          )}


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
                <div
                  key={player.id}
                  className={`${styles.playerRow} ${draggingId === player.id ? styles.dragging : ""}`}
                  draggable
                  onDragStart={(event) => {
                    event.dataTransfer.setData("text/plain", String(player.id));
                    event.dataTransfer.effectAllowed = "move";
                    prepareDragPlayer(player);
                  }}
                  onDragEnd={clearDragState}
                >
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
