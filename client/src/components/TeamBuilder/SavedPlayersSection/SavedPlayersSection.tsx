import { useState } from "react";
import { Trash2 } from "lucide-react";
import { SavedPlayer, PlayerValueScore } from "@/api/players";
import { Card } from "@/components";
import { PlayerRow } from "../PlayerRow/PlayerRow";
import styles from "./SavedPlayersSection.module.css";

type SavedPlayersSectionProps = {
  players: SavedPlayer[];
  assignedIds: Set<number>;
  draggingId: number | null;
  deletingPlayerIds: Set<number>;
  onPrepareDrag: (player: SavedPlayer) => void;
  onClearDrag: () => void;
  onDeletePlayer: (player: SavedPlayer) => void | Promise<void>;
  playerScores?: PlayerValueScore[];
  benchReplacements?: Map<number, { replacesPosition: string; replacesName: string; delta: number }>;
  headerAction?: React.ReactNode;
};

/**
 * Render the "Saved Players" UI with separate Lineup and Bench sections, sorting, drag-and-drop, and per-player actions.
 *
 * @param players - Array of saved players to display.
 * @param assignedIds - Set of player IDs currently assigned to the active lineup.
 * @param draggingId - ID of the player currently being dragged (if any).
 * @param deletingPlayerIds - Set of player IDs that are in the deleting state.
 * @param onPrepareDrag - Callback invoked with a player when a drag is started.
 * @param onClearDrag - Callback invoked when a drag operation ends.
 * @param onDeletePlayer - Callback invoked with a player when the delete action is confirmed.
 * @param playerScores - Optional list of player score objects used to display and sort by adjustment_score; missing scores are treated as 0.
 * @param benchReplacements - Optional map of bench player ID to replacement info (position, name, delta) shown alongside bench players.
 * @param headerAction - Optional React node rendered in the card header (e.g., action button).
 * @returns The rendered Saved Players section as a Card containing lineup and bench lists, sort controls, and per-player controls.
 */
export function SavedPlayersSection({
  players,
  assignedIds,
  draggingId,
  deletingPlayerIds,
  onPrepareDrag,
  onClearDrag,
  onDeletePlayer,
  playerScores = [],
  benchReplacements = new Map(),
  headerAction,
}: SavedPlayersSectionProps) {
  const [benchSortBy, setBenchSortBy] = useState<'name' | 'score'>('name');
  
  // Split players into playing (with positions) and bench (without positions)
  const playingPlayers = players.filter(p => p.position != null && p.position !== '');
  const benchPlayers = players.filter(p => !p.position || p.position === '');
  
  // Sort playing players by score (descending)
  const sortedPlayingPlayers = [...playingPlayers].sort((a, b) => {
    const scoreA = playerScores.find(s => s.id === a.id)?.adjustment_score ?? 0;
    const scoreB = playerScores.find(s => s.id === b.id)?.adjustment_score ?? 0;
    return scoreB - scoreA; // Higher scores first
  });
  
  // Sort bench players by selected criteria
  const sortedBenchPlayers = [...benchPlayers].sort((a, b) => {
    if (benchSortBy === 'score') {
      const scoreA = playerScores.find(s => s.id === a.id)?.adjustment_score ?? 0;
      const scoreB = playerScores.find(s => s.id === b.id)?.adjustment_score ?? 0;
      return scoreB - scoreA; // Higher scores first
    } else {
      const lastNameA = a.name.split(' ')[1] || a.name;
      const lastNameB = b.name.split(' ')[1] || b.name;
      return lastNameA.localeCompare(lastNameB);
    }
  });
  
  const subtitle = `${playingPlayers.length} lineup • ${benchPlayers.length} bench`;
  
  const renderPlayingPlayerCard = (player: SavedPlayer) => {
    const scoreData = playerScores.find(s => s.id === player.id);
    const adjustmentScore = scoreData?.adjustment_score;
    const isDeleting = deletingPlayerIds.has(player.id);

    return (
      <div key={player.id} className={styles.playingPlayerCard}>
        <img src={player.image_url ?? ""} alt={player.name} className={styles.playingPlayerAvatar} />
        <div className={styles.playingPlayerInfo}>
          <div className={styles.playingPlayerName}>{player.name}</div>
          {player.position && (
            <span className={styles.playingPlayerPosition}>{player.position}</span>
          )}
        </div>
        {adjustmentScore !== undefined && (
          <div className={`${styles.playingPlayerScore} ${adjustmentScore >= 0 ? styles.scorePositive : styles.scoreNegative}`}>
            {adjustmentScore >= 0 ? "+" : ""}{adjustmentScore.toFixed(2)}
          </div>
        )}
        <button
          className={styles.deletePlayerButton}
          disabled={isDeleting}
          onClick={() => onDeletePlayer(player)}
          title="Delete from saved players"
        >
          {isDeleting ? "..." : <Trash2 size={16} />}
        </button>
      </div>
    );
  };

  const renderBenchPlayerRow = (player: SavedPlayer) => {
    const alreadyAssigned = assignedIds.has(player.id);
    const isDeleting = deletingPlayerIds.has(player.id);
    const scoreData = playerScores.find(s => s.id === player.id);
    const adjustmentScore = scoreData?.adjustment_score;
    const replacement = benchReplacements.get(player.id);
    
    // Create a player object with position for display (bench players don't have position set)
    const playerWithPosition = { ...player };

    return (
      <PlayerRow
        key={player.id}
        player={playerWithPosition}
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
        adjustmentScore={adjustmentScore}
        replacementInfo={replacement ? `Replacing ${replacement.replacesPosition}` : undefined}
      />
    );
  };

  return (
    <Card title="Saved Players" subtitle={subtitle} headerAction={headerAction}>
      <div className={styles.playerScroller}>
        {players.length === 0 ? (
          <div className={styles.emptyState}>
            <strong>No saved players</strong>
            <span>Search for players and add them to your team.</span>
          </div>
        ) : (
          <>
            {sortedPlayingPlayers.length > 0 && (
              <div className={styles.playerSection}>
                <div className={styles.sectionHeader}>Lineup</div>
                <div className={styles.playingPlayersGrid}>
                  {sortedPlayingPlayers.map(renderPlayingPlayerCard)}
                </div>
              </div>
            )}
            
            {sortedBenchPlayers.length > 0 && (
              <div className={styles.playerSection}>
                <div className={styles.benchHeader}>
                  <div className={styles.sectionHeader}>Bench</div>
                  <div className={styles.sortToggle}>
                    <button
                      className={`${styles.sortButton} ${benchSortBy === 'name' ? styles.sortButtonActive : ''}`}
                      onClick={() => setBenchSortBy('name')}
                    >
                      Name
                    </button>
                    <button
                      className={`${styles.sortButton} ${benchSortBy === 'score' ? styles.sortButtonActive : ''}`}
                      onClick={() => setBenchSortBy('score')}
                    >
                      Score
                    </button>
                  </div>
                </div>
                <div className={styles.benchPlayersList}>
                  {sortedBenchPlayers.map(renderBenchPlayerRow)}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
}
