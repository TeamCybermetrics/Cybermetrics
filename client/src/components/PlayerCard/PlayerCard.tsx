import { useEffect, useState } from "react";
import { PlayerDetail } from "@/api/players";
import { playerActions } from "@/actions/players";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import styles from "./PlayerCard.module.css";

interface PlayerCardProps {
  playerId: number;
  onClose: () => void;
}

export default function PlayerCard({ playerId, onClose }: PlayerCardProps) {
  const [player, setPlayer] = useState<PlayerDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPlayerDetail = async () => {
      setIsLoading(true);
      const result = await playerActions.getPlayerDetail(playerId);
      
      if (result.success) {
        setPlayer(result.data);
      } else {
        setError(result.error);
      }
      
      setIsLoading(false);
    };

    fetchPlayerDetail();
  }, [playerId]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.modal}>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>

        {isLoading && (
          <div className={styles.loading}>
            <Spinner />
          </div>
        )}

        {error && (
          <div className={styles.error}>
            <p>Error loading player details</p>
            <p className={styles.errorMessage}>{error}</p>
            <Button onClick={onClose} variant="secondary">Close</Button>
          </div>
        )}

        {player && !isLoading && (
          <div className={styles.content}>
            <div className={styles.header}>
              <img
                src={player.image_url}
                alt={player.name}
                className={styles.playerImage}
                onError={(e) => {
                  e.currentTarget.src = 'https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current';
                }}
              />
              <div className={styles.headerInfo}>
                <h2 className={styles.playerName}>{player.name}</h2>
                {player.years_active && <p className={styles.yearsActive}>{player.years_active}</p>}
              </div>
            </div>

            <div className={styles.details}>
              <div className={styles.detailRow}>
                <span className={styles.label}>MLB ID:</span>
                <span className={styles.value}>{player.id}</span>
              </div>
              
              {player.first_name && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>First Name:</span>
                  <span className={styles.value}>{player.first_name}</span>
                </div>
              )}

              {player.last_name && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>Last Name:</span>
                  <span className={styles.value}>{player.last_name}</span>
                </div>
              )}

              {player.mlb_played_first && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>First Year in MLB:</span>
                  <span className={styles.value}>{player.mlb_played_first}</span>
                </div>
              )}

              {player.mlb_played_last && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>Last Year in MLB:</span>
                  <span className={styles.value}>{player.mlb_played_last}</span>
                </div>
              )}

              {player.key_retro && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>Retrosheet ID:</span>
                  <span className={styles.value}>{player.key_retro}</span>
                </div>
              )}

              {player.key_bbref && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>Baseball Reference ID:</span>
                  <span className={styles.value}>{player.key_bbref}</span>
                </div>
              )}

              {player.key_fangraphs && (
                <div className={styles.detailRow}>
                  <span className={styles.label}>Fangraphs ID:</span>
                  <span className={styles.value}>{player.key_fangraphs}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

