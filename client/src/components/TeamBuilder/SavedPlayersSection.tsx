import { SavedPlayer } from "@/api/players";
import { PlayerRow } from "./PlayerRow";
import styles from "./SavedPlayersSection.module.css";
import { DiamondPosition } from "./constants";

type SavedPlayersSectionProps = {
  players: SavedPlayer[];
  assignedIds: Set<number>;
  draggingId: number | null;
  savingPlayerIds: Set<number>;
  deletingPlayerIds: Set<number>;
  activePosition: DiamondPosition | null;
  onPrepareDrag: (player: SavedPlayer) => void;
  onClearDrag: () => void;
  onAddPlayer: (player: SavedPlayer) => void | Promise<void>;
  onDeletePlayer: (player: SavedPlayer) => void | Promise<void>;
};

export function SavedPlayersSection({
  players,
  assignedIds,
  draggingId,
  savingPlayerIds,
  deletingPlayerIds,
  activePosition,
  onPrepareDrag,
  onClearDrag,
  onAddPlayer,
  onDeletePlayer,
}: SavedPlayersSectionProps) {
  return (
    <div className={styles.displayBox}>
      <div className={styles.sectionHeader}>
        <h3>Saved Players</h3>
        <span>{players.length}</span>
      </div>
      <div className={styles.playerScroller}>
        {players.length === 0 ? (
          <div className={styles.emptyState}>
            <strong>No saved players</strong>
            <span>Search for players and add them to your team.</span>
          </div>
        ) : (
          players.map((player) => {
            const alreadyAssigned = assignedIds.has(player.id);
            const isDeleting = deletingPlayerIds.has(player.id);

            return (
              <PlayerRow
                key={player.id}
                player={player}
                isDragging={draggingId === player.id}
                draggable={!alreadyAssigned}
                onDragStart={() => !alreadyAssigned && onPrepareDrag(player)}
                onDragEnd={onClearDrag}
                showDelete
                deleteDisabled={alreadyAssigned || isDeleting}
                deleteLabel={isDeleting ? "Deleting…" : "Delete"}
                deleteTitle={
                  alreadyAssigned
                    ? "Remove from the lineup before deleting"
                    : "Delete from saved players"
                }
                onDelete={() => onDeletePlayer(player)}
                addDisabled={
                  alreadyAssigned ||
                  !activePosition ||
                  savingPlayerIds.has(player.id)
                }
                addLabel={
                  alreadyAssigned
                    ? "Assigned"
                    : savingPlayerIds.has(player.id)
                    ? "Saving..."
                    : "Add"
                }
                addTitle={
                  alreadyAssigned
                    ? "Already assigned"
                    : !activePosition
                    ? "Select a position first"
                    : "Add to active position"
                }
                onAdd={() => void onAddPlayer(player)}
              />
            );
          })
        )}
      </div>
    </div>
  );
}

