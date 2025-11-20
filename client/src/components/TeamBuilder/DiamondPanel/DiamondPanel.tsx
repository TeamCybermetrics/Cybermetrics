import { DragEvent } from "react";
import { SavedPlayer } from "@/api/players";
import { Card } from "@/components";
import styles from "./DiamondPanel.module.css";
import {
  DiamondPosition,
  positionCoordinates,
  positionOrder,
  staticSpots,
} from "../constants";

type DiamondPanelProps = {
  lineup: Record<DiamondPosition, SavedPlayer | null>;
  activePosition: DiamondPosition | null;
  dropTarget: DiamondPosition | null;
  dragPlayer: SavedPlayer | null;
  onSelectPosition: (position: DiamondPosition) => void;
  onDragOverPosition: (position: DiamondPosition) => void;
  onDragLeavePosition: () => void;
  onDropOnPosition: (event: DragEvent<HTMLButtonElement>, position: DiamondPosition) => void;
  onPrepareDrag: (player: SavedPlayer, position: DiamondPosition) => void;
  onClearDragState: () => void;
  onClearSlot: (position: DiamondPosition) => void;
  onSaveTeam?: () => void;
};

/**
 * Renders an interactive diamond-shaped lineup editor showing positions, assigned players, and drag-and-drop controls.
 *
 * The component displays each position as a node on a diamond diagram, allows selecting positions, dragging assigned
 * players between positions, clearing slots, and optionally saving the lineup.
 *
 * @param lineup - Mapping of DiamondPosition to a SavedPlayer or `null` for empty slots.
 * @param activePosition - Currently selected DiamondPosition, or `null` if none.
 * @param dropTarget - Position currently highlighted as a valid drop target, or `null`.
 * @param dragPlayer - The SavedPlayer being dragged, or `null` when no drag is active.
 * @param onSelectPosition - Called when a position node is clicked with the selected position.
 * @param onDragOverPosition - Called when a draggable item is moved over a position; receives the position.
 * @param onDragLeavePosition - Called when a draggable item leaves a position.
 * @param onDropOnPosition - Called when a dragged player is dropped onto a position; receives the drop event and target position.
 * @param onPrepareDrag - Called to begin dragging a player; receives the player and its origin position.
 * @param onClearDragState - Called when a drag operation ends or is cancelled to clear drag state.
 * @param onClearSlot - Called to clear the player assigned to the given position.
 * @param onSaveTeam - Optional handler invoked when the "Save Lineup" button is clicked.
 * @returns The rendered React element for the diamond lineup panel.
 */
export function DiamondPanel({
  lineup,
  activePosition,
  dropTarget,
  dragPlayer,
  onSelectPosition,
  onDragOverPosition,
  onDragLeavePosition,
  onDropOnPosition,
  onPrepareDrag,
  onClearDragState,
  onClearSlot,
  onSaveTeam,
}: DiamondPanelProps) {
  return (
    <Card title="Your Lineup" subtitle="Select a position, then add or drag a player.">
      <div className={styles.diamondContainer}>
        {activePosition && (
          <div className={styles.activeBadge}>
            Active: {activePosition}
          </div>
        )}
        <div className={styles.diamond}>
        <svg className={styles.diamondLines} viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Continuous foul lines from home plate through bases to outfield arc */}
          {/* <line x1="50" y1="95" x2="10" y2="38" stroke="currentColor" strokeWidth="0.5" /> */}
          <line x1="50" y1="95" x2="1" y2="38" stroke="currentColor" strokeWidth="0.5" />
          {/* <line x1="30" y1="70" x2="10" y2="38" stroke="currentColor" strokeWidth="0.5" /> */}
          <line x1="50" y1="95" x2="99" y2="38" stroke="currentColor" strokeWidth="0.5" />
          {/* <line x1="70" y1="70" x2="90" y2="38" stroke="currentColor" strokeWidth="0.5" /> */}
          
          {/* Outfield arc */}
          <path
            d="M 1 38 Q 50 -20 99 38"
            fill="none"
            stroke="currentColor"
            strokeWidth="0.5"
          />
          
          {/* Base paths connecting bases */}
          <line x1="26" y1="66" x2="50" y2="42" stroke="currentColor" strokeWidth="0.5" />
          <line x1="50" y1="42" x2="74" y2="66" stroke="currentColor" strokeWidth="0.5" />
          
          {/* Home plate (pentagon) - point at top touching base paths */}

          {/* points="50,95 47,98 47,100 53,100 53,98" */}
          <polygon
            points="50,98 47,96 47,93 53,93 53,96"
            fill="currentColor"
            stroke="currentColor"
            strokeWidth="0.3"
          />
          
          {/* First base (square) */}
          <rect x="72" y="64" width="4" height="4" fill="currentColor" stroke="currentColor" strokeWidth="0.3" />

          {/* Second base (square) */}
          {/* 53 */}
          <rect x="48" y="40" width="4" height="4" fill="currentColor" stroke="currentColor" strokeWidth="0.3" />

          {/* Third base (square) */}
          <rect x="24" y="64" width="4" height="4" fill="currentColor" stroke="currentColor" strokeWidth="0.3" />
          
        </svg>

        {positionOrder.map((pos) => {
          const assigned = lineup[pos];
          const isActive = activePosition === pos;
          const canDrop = dragPlayer && !assigned;
          return (
            <div
              key={pos}
              className={`${styles.positionNode} ${assigned ? styles.filled : ""} ${
                isActive ? styles.active : ""
              } ${canDrop && dropTarget === pos ? styles.droppable : ""}`}
              style={positionCoordinates[pos]}
            >
              <button
                type="button"
                className={styles.positionTrigger}
                onClick={() => onSelectPosition(pos)}
                onDragOver={(event) => {
                  event.preventDefault();
                  onDragOverPosition(pos);
                }}
                onDragLeave={() => onDragLeavePosition()}
                onDrop={(event) => onDropOnPosition(event, pos)}
                draggable={!!assigned}
                onDragStart={() => assigned && onPrepareDrag(assigned, pos)}
                onDragEnd={onClearDragState}
                aria-label={`Position ${pos}`}
              >
                {assigned ? (
                  <div className={styles.positionPlayer}>
                    <img src={assigned.image_url} alt={assigned.name} />
                    <div className={styles.positionName}>{assigned.name}</div>
                  </div>
                ) : (
                  <>
                    <div className={styles.positionLabel}>{pos}</div>
                    <div style={{ fontSize: 12, opacity: 0.7 }}>Drop or click</div>
                  </>
                )}
              </button>

              {assigned && (
                <button
                  className={styles.clearSlot}
                  onClick={() => onClearSlot(pos)}
                  title="Clear"
                >
                  ×
                </button>
              )}
            </div>
          );
        })}

        {staticSpots.map((spot) => (
          <div
            key={spot.label}
            className={`${styles.positionNode} ${styles.staticPosition}`}
            style={{ top: spot.top, left: spot.left }}
            aria-hidden="true"
          >
            <div className={styles.positionLabel}>{spot.label}</div>
            <div className={styles.staticHint}>Pitcher</div>
          </div>
        ))}
        </div>
      </div>

      {onSaveTeam && (
        <button className={styles.saveButton} onClick={onSaveTeam}>
          Save Lineup
        </button>
      )}
    </Card>
  );
}
