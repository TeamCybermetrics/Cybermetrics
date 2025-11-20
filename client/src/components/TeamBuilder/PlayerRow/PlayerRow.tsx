import { SavedPlayer } from "@/api/players";
import styles from "./PlayerRow.module.css";

type PlayerRowProps = {
  player: SavedPlayer;
  isDragging?: boolean;
  draggable?: boolean;
  onDragStart?: () => void;
  onDragEnd?: () => void;
  showDelete?: boolean;
  deleteDisabled?: boolean;
  deleteLabel?: string;
  deleteTitle?: string;
  onDelete?: () => void;
  addDisabled?: boolean;
  addLabel: string;
  addTitle?: string;
  onAdd?: () => void;
  adjustmentScore?: number;
  replacementInfo?: string;
};

export function PlayerRow({
  player,
  isDragging = false,
  draggable = true,
  onDragStart,
  onDragEnd,
  showDelete = true,
  deleteDisabled = false,
  deleteLabel = "Delete",
  deleteTitle,
  onDelete,
  addDisabled = false,
  addLabel,
  addTitle,
  onAdd,
  adjustmentScore,
  replacementInfo,
}: PlayerRowProps) {
  return (
    <div
      className={`${styles.playerRow} ${isDragging ? styles.dragging : ""}`}
      draggable={draggable}
      onDragStart={draggable ? onDragStart : undefined}
      onDragEnd={onDragEnd}
    >
      <div className={styles.playerProfile}>
        <img src={player.image_url ?? ""} alt={player.name} />
        <div className={styles.playerInfo}>
          <div className={styles.playerNameRow}>
            <p className={styles.playerName}>{player.name}</p>
            {player.position && (
              <span className={styles.positionBadge}>{player.position}</span>
            )}
          </div>
          {adjustmentScore !== undefined && (
            <p className={`${styles.adjustmentScore} ${adjustmentScore >= 0 ? styles.scorePositive : styles.scoreNegative}`}>
              {adjustmentScore >= 0 ? "+" : ""}{adjustmentScore.toFixed(2)}
            </p>
          )}
          {replacementInfo && (
            <p className={styles.replacementInfo}>
              {replacementInfo}
            </p>
          )}
        </div>
      </div>

      <div className={styles.playerActions}>
        {showDelete && (
          <button
            className={styles.deletePlayerButton}
            disabled={deleteDisabled}
            onClick={onDelete}
            title={deleteTitle}
          >
            {deleteLabel}
          </button>
        )}
        <button
          className={styles.addButton}
          disabled={addDisabled}
          onClick={onAdd}
          title={addTitle}
        >
          {addLabel}
        </button>
      </div>
    </div>
  );
}

