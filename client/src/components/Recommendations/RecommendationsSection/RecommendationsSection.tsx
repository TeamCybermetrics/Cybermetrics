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

