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
  addLabel?: string;
  addTitle?: string;
  onAdd?: () => void;
  adjustmentScore?: number;
  replacementInfo?: string;
};

/**
 * Render a player's row containing profile, optional position, adjustment score, replacement info, and action buttons.
 *
 * @param player - The player to display.
 * @param isDragging - Whether the row is currently being dragged (applies dragging style).
 * @param draggable - Whether the row is draggable.
 * @param onDragStart - Callback invoked when dragging starts (only wired if `draggable` is true).
 * @param onDragEnd - Callback invoked when dragging ends.
 * @param showDelete - Whether to render the delete button.
 * @param deleteDisabled - Whether the delete button is disabled.
 * @param deleteLabel - Text for the delete button.
 * @param deleteTitle - Tooltip/title for the delete button.
 * @param onDelete - Callback invoked when the delete button is clicked.
 * @param addDisabled - Whether the add button is disabled.
 * @param addLabel - Text for the add button; when omitted the add button is not rendered.
 * @param addTitle - Tooltip/title for the add button.
 * @param onAdd - Callback invoked when the add button is clicked.
 * @param adjustmentScore - Optional numeric adjustment displayed with a sign and two decimal places; positive and negative values receive different visual styles.
 * @param replacementInfo - Optional auxiliary text shown beneath the player info.
 * @returns The JSX element representing the player's row.
 */
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
        {addLabel && (
          <button
            className={styles.addButton}
            disabled={addDisabled}
            onClick={onAdd}
            title={addTitle}
          >
            {addLabel}
          </button>
        )}
      </div>
    </div>
  );
}
