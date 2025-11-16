import { SavedPlayer } from "@/api/players";
import { PlayerRow } from "../PlayerRow/PlayerRow";
import styles from "./SearchResultsSection.module.css";

type SearchResultsSectionProps = {
  players: SavedPlayer[];
  savedPlayerIds?: Set<number>;
  assignedIds?: Set<number>;
  draggingId?: number | null;
  savingPlayerIds?: Set<number>;
  allowAddSaved?: boolean;
  addLabel?: string;
  onPrepareDrag?: (player: SavedPlayer) => void;
  onClearDrag?: () => void;
  onSavePlayer: (player: SavedPlayer) => void | Promise<void>;
};

export function SearchResultsSection({
  players,
  savedPlayerIds,
  assignedIds,
  draggingId,
  savingPlayerIds,
  allowAddSaved = false,
  addLabel = "Add to lineup",
  onPrepareDrag,
  onClearDrag,
  onSavePlayer,
}: SearchResultsSectionProps) {
  return (
    <section className={`${styles.displayBox} ${styles.searchResultsSection}`}>
      <div className={styles.sectionHeader}>
        <h3>Search Results</h3>
        <span>{players.length}</span>
      </div>
      <div className={`${styles.playerScroller} ${styles.searchResultsScroller}`}>
        {players.length === 0 ? (
          <div className={styles.emptyState}>
            <strong>No players found</strong>
            <span>Try a different search.</span>
          </div>
        ) : (
          players.map((player) => {
            const alreadyAssigned = assignedIds?.has(player.id) ?? false;
            const alreadySaved = savedPlayerIds?.has(player.id) ?? false;
            const isSaving = savingPlayerIds?.has(player.id) ?? false;
            const addDisabled = isSaving || (!allowAddSaved && alreadySaved);

            return (
              <PlayerRow
                key={player.id}
                player={player}
                isDragging={draggingId === undefined ? false : draggingId === player.id}
                draggable={!!onPrepareDrag && !alreadyAssigned}
                onDragStart={() => onPrepareDrag && !alreadyAssigned && onPrepareDrag(player)}
                onDragEnd={onClearDrag}
                showDelete={false}
                addDisabled={addDisabled}
                addLabel={isSaving ? "Saving..." : addLabel}
                addTitle={addDisabled ? "Already in your saved players" : "Add this player to your lineup"}
                onAdd={() => {
                  if (!addDisabled) {
                    void onSavePlayer(player);
                  }
                }}
              />
            );
          })
        )}
      </div>
    </section>
  );
}
