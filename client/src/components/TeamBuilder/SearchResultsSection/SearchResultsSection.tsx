import { SavedPlayer } from "@/api/players";
import { PlayerRow } from "../PlayerRow/PlayerRow";
import styles from "./SearchResultsSection.module.css";

type SearchResultsSectionProps = {
  players: SavedPlayer[];
  savedPlayerIds: Set<number>;
  assignedIds: Set<number>;
  draggingId: number | null;
  savingPlayerIds: Set<number>;
  deletingPlayerIds?: Set<number>;
  onPrepareDrag: (player: SavedPlayer) => void;
  onClearDrag: () => void;
  onSavePlayer: (player: SavedPlayer) => void | Promise<void>;
  onDeletePlayer?: (player: SavedPlayer) => void | Promise<void>;
};

export function SearchResultsSection({
  players,
  savedPlayerIds,
  assignedIds,
  draggingId,
  savingPlayerIds,
  deletingPlayerIds = new Set(),
  onPrepareDrag,
  onClearDrag,
  onSavePlayer,
  onDeletePlayer,
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
            const alreadyAssigned = assignedIds.has(player.id);
            const alreadySaved = savedPlayerIds.has(player.id);
            const isSaving = savingPlayerIds.has(player.id);
            const isDeleting = deletingPlayerIds.has(player.id);

            return (
              <PlayerRow
                key={player.id}
                player={player}
                isDragging={draggingId === player.id}
                draggable={!alreadyAssigned}
                onDragStart={() => !alreadyAssigned && onPrepareDrag(player)}
                onDragEnd={onClearDrag}
                showDelete={alreadySaved}
                deleteDisabled={isDeleting}
                deleteLabel={isDeleting ? "Removing..." : "Remove"}
                deleteTitle="Remove from saved players"
                onDelete={onDeletePlayer ? () => void onDeletePlayer(player) : undefined}
                addLabel={
                  alreadySaved ? undefined : isSaving ? "Saving..." : "Add to Saved"
                }
                addTitle={
                  alreadySaved
                    ? undefined
                    : "Add this player to your saved players"
                }
                addDisabled={isSaving}
                onAdd={() => {
                  if (!alreadySaved && !isSaving) {
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

