import type { TeamWeaknessResponse } from "@/api/players";
import { Card } from "@/components";
import styles from "@/features/recommendations/RecommendationsView.module.css";

type StatKey = { key: keyof TeamWeaknessResponse; label: string };

type Props = {
  statKeys: StatKey[];
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  loading: boolean;
  error: string | null;
  formatValue: (value: number) => string;
};

export function WeaknessDeltasCard({
  statKeys,
  baselineWeakness,
  currentWeakness,
  loading,
  error,
  formatValue
}: Props) {
  const hasData = baselineWeakness && currentWeakness;

  return (
    <Card title="Changes in Team Weakness">
      {loading && <div className={styles.placeholder}>Calculating…</div>}
      {error && <div className={styles.recommendError}>{error}</div>}
      {!loading && !error && hasData ? (
        <div className={styles.weaknessGrid}>
          {statKeys.map(({ key, label }) => {
            const delta = currentWeakness![key] - baselineWeakness![key];
            const cls = delta >= 0 ? styles.weakScoreGreen : styles.weakScoreRed;
            return (
              <div key={label}>
                <div className={styles.weakLabel}>{label}</div>
                <div className={cls}>
                  {delta >= 0 ? "+" : ""}
                  {formatValue(delta)}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        !loading &&
        !error && <div className={styles.placeholder}>Add players to see changes.</div>
      )}
    </Card>
  );
}
