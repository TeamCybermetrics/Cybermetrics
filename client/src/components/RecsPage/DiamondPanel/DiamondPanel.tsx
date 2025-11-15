import { DragEvent } from "react";
import { SavedPlayer } from "@/api/players";
import styles from "./DiamondPanel.module.css";
import {
  DiamondPosition,
  positionCoordinates,
  positionOrder,
  staticSpots,
} from "@/components/TeamBuilder/constants";

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
    <section className={styles.panel}>
      <div className={styles.panelHeader}>
        <div>
          <h2>Your lineup</h2>
          <p>Select a position, then add or drag a player.</p>
        </div>
        <span className={styles.positionHint}>
          {activePosition ? `Active: ${activePosition}` : "Pick a position"}
        </span>
      </div>

      <div className={styles.diamond}>
        <svg className={styles.diamondLines} viewBox="0 0 100 100" preserveAspectRatio="none">
          <rect x="5" y="5" width="90" height="90" rx="8" ry="8" />
          <line x1="50" y1="10" x2="10" y2="50" />
          <line x1="50" y1="10" x2="90" y2="50" />
          <line x1="10" y1="50" x2="50" y2="90" />
          <line x1="50" y1="90" x2="90" y2="50" />
          <circle cx="50" cy="12" r="2" />
          <circle cx="50" cy="50" r="2" />
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

      {onSaveTeam && (
        <button className={styles.saveButton} onClick={onSaveTeam}>
          Save Lineup
        </button>
      )}
    </section>
  );
}

