import { SavedPlayer } from "@/api/players";
import type { DiamondPosition } from "@/components/TeamBuilder/constants";
import styles from "./RecommendationsSection.module.css";

type RecommendationsSectionProps = {
  players: SavedPlayer[];
  savedPlayerIds?: Set<number>;
  savingPlayerIds?: Set<number>;
  deletingPlayerIds?: Set<number>;
  onSavePlayer: (player: SavedPlayer, position?: DiamondPosition) => void | Promise<void>;
  onDeletePlayer?: (player: SavedPlayer) => void | Promise<void>;
  allowAddSaved?: boolean;
  addLabel?: string;
};

/**
 * Render a list of recommended players with controls to add or remove each player.
 *
 * @param players - Player suggestions to render.
 * @param savedPlayerIds - IDs of players already saved; presence enables the remove action for that item.
 * @param savingPlayerIds - IDs of players currently being saved; those items show "Saving..." and are disabled.
 * @param deletingPlayerIds - IDs of players currently being deleted; those items show "Removing..." and are disabled.
 * @param onSavePlayer - Callback invoked when the add action is triggered for a player.
 * @param onDeletePlayer - Optional callback invoked when the remove action is triggered for a saved player.
 * @param allowAddSaved - When true, allows adding players that are already saved; when false, add is disabled for saved players unless a remove handler exists.
 * @param addLabel - Label text used for the add action when not saving or removing.
 * @returns The rendered recommendations list element, or `null` when `players` is empty.
 */
export function RecommendationsSection({
  players,
  savedPlayerIds,
  savingPlayerIds,
  deletingPlayerIds = new Set(),
  onSavePlayer,
  onDeletePlayer,
  allowAddSaved = false,
  addLabel = "Add to lineup",
}: RecommendationsSectionProps) {
  if (players.length === 0) {
    return null;
  }

  return (
    <ul className={styles.recommendList}>
      {players.map((player) => {
        const alreadySaved = savedPlayerIds?.has(player.id) ?? false;
        const isSaving = savingPlayerIds?.has(player.id) ?? false;
        const isDeleting = deletingPlayerIds.has(player.id);
        const showRemove = alreadySaved && onDeletePlayer;
        const disabled = isSaving || isDeleting || (!allowAddSaved && alreadySaved && !showRemove);
        const label = isDeleting ? "Removing..." : showRemove ? "Remove" : isSaving ? "Saving..." : addLabel;

        const savedPlayer: SavedPlayer = {
          id: player.id,
          name: player.name,
          image_url: player.image_url,
          years_active: player.years_active,
        };

        return (
          <li key={player.id} className={styles.recommendItem}>
            <div className={styles.recommendPlayerInfo}>
              <img src={player.image_url} alt={player.name} />
              <div>
                <div className={styles.recommendName}>{player.name}</div>
                <div className={styles.recommendMeta}>{player.years_active}</div>
              </div>
            </div>
            <div className={styles.recommendActions}>
              <span className={styles.recommendScore}>
                {/* Impact Score: {player.score.toFixed(1)} */}
              </span>
              <button
                className={styles.addButton}
                disabled={disabled}
                onClick={() => {
                  if (!disabled) {
                    if (showRemove) {
                      void onDeletePlayer!(savedPlayer);
                    } else {
                      void onSavePlayer(savedPlayer);
                    }
                  }
                }}
              >
                {label}
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
