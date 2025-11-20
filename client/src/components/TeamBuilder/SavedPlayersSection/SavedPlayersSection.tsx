import { SavedPlayer } from "@/api/players";
import { Card } from "@/components";
import { PlayerRow } from "../PlayerRow/PlayerRow";
import styles from "./SavedPlayersSection.module.css";
import { DiamondPosition } from "../constants";

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
  const subtitle = `${players.length} player${players.length !== 1 ? 's' : ''}`;
  
  // Sort players alphabetically by last name (second name after first space)
  const sortedPlayers = [...players].sort((a, b) => {
    const lastNameA = a.name.split(' ')[1] || a.name;
    const lastNameB = b.name.split(' ')[1] || b.name;
    return lastNameA.localeCompare(lastNameB);
  });
  
  return (
    <Card title="Saved Players" subtitle={subtitle}>
      <div className={styles.playerScroller}>
        {players.length === 0 ? (
          <div className={styles.emptyState}>
            <strong>No saved players</strong>
            <span>Search for players and add them to your team.</span>
          </div>
        ) : (
          sortedPlayers.map((player) => {
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
                    ? "Already Assigned"
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
    </Card>
  );
}

