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

/**
 * Render the Search Results UI containing a scrollable list of players with add, delete, and drag controls.
 *
 * Renders an empty state when `players` is empty; otherwise renders a PlayerRow for each player.
 * Per-player control states (draggable, add/delete enabled state and labels, dragging indicator) are derived from the provided ID sets.
 *
 * @param players - The list of players to display.
 * @param savedPlayerIds - IDs of players already saved; saved players show the delete control instead of an add label.
 * @param assignedIds - IDs of players already assigned; assigned players are not draggable.
 * @param draggingId - ID of the player currently being dragged, or `null` when none.
 * @param savingPlayerIds - IDs of players currently being saved; saving players have the add control disabled and labeled accordingly.
 * @param deletingPlayerIds - IDs of players currently being deleted; deleting players have the delete control disabled and labeled accordingly.
 * @param onPrepareDrag - Called with a player to initiate dragging for that player.
 * @param onClearDrag - Called when a drag operation ends to clear drag state.
 * @param onSavePlayer - Called to add a player to saved players.
 * @param onDeletePlayer - Optional; called to remove a saved player when provided.
 * @returns The section element containing the search results list (or empty state).
 */
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
