import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import styles from "./RecommendationsSection.module.css";

type RecommendationsSectionProps = {
  players: PlayerSearchResult[];
  savedPlayerIds: Set<number>;
  savingPlayerIds: Set<number>;
  onSavePlayer: (player: SavedPlayer) => void | Promise<void>;
};

export function RecommendationsSection({
  players,
  savedPlayerIds,
  savingPlayerIds,
  onSavePlayer,
}: RecommendationsSectionProps) {
  if (players.length === 0) {
    return null;
  }

  return (
    <ul className={styles.recommendList}>
      {players.map((player) => {
        const alreadySaved = savedPlayerIds.has(player.id);
        const isSaving = savingPlayerIds.has(player.id);
        const disabled = alreadySaved || isSaving;
        const label = alreadySaved ? "Already Saved" : isSaving ? "Saving..." : "Add to Saved";

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
                    void onSavePlayer(savedPlayer);
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

