import type { TeamWeaknessResponse } from "@/api/players";
import { Card } from "@/components";
import styles from "@/components/Recommendations/RecommendationsView/RecommendationsView.module.css";

type StatKey = { key: keyof TeamWeaknessResponse; label: string };

type Props = {
  statKeys: StatKey[];
  baselineWeakness: TeamWeaknessResponse | null;
  currentWeakness: TeamWeaknessResponse | null;
  loading: boolean;
  error: string | null;
  formatValue: (value: number) => string;
};

/**
 * Renders a card showing per-stat changes in team weakness or an appropriate placeholder.
 *
 * Renders one of: a loading placeholder, an error message, a grid of deltas for each stat when both
 * baseline and current weakness data are available, or a prompt to add players when data is missing.
 *
 * @param statKeys - Array of stat descriptors; each item maps a key from `TeamWeaknessResponse` to a display label.
 * @param baselineWeakness - Baseline team weakness values or `null` when unavailable.
 * @param currentWeakness - Current team weakness values or `null` when unavailable.
 * @param loading - When `true`, shows a calculating placeholder instead of data.
 * @param error - When set, displays the error message inside the card.
 * @param formatValue - Formats a numeric delta for display.
 * @returns The rendered Card element containing the appropriate UI for loading, error, data, or empty state.
 */
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