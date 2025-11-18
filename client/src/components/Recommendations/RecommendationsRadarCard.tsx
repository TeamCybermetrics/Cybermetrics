import PercentileRadar from "@/components/Radar/PercentileRadar";
import { RING_FRACTIONS, RING_LABELS, Z_SCORE_CONFIG } from "@/utils/zScoreRadar";
import styles from "@/features/recommendations/RecommendationsView.module.css";

type Axis = { label: string };

type Props = {
  axes: Axis[];
  baselineFractions: number[];
  currentFractions: number[];
  highlightOrder: number[];
  loading: boolean;
  error: string | null;
  legendItems?: string[];
};

export function RecommendationsRadarCard({
  axes,
  baselineFractions,
  currentFractions,
  highlightOrder,
  loading,
  error,
  legendItems
}: Props) {
  return (
    <div className={styles.radarCard}>
      <div className={styles.radarHeader}>Before/After</div>
      <div className={styles.radarSubheader}>Weakness radar</div>
      {loading && <div className={styles.radarPlaceholder}>Calculating…</div>}
      {error && <div className={styles.radarPlaceholder}>{error}</div>}
      {!loading && !error && currentFractions.length > 0 ? (
        <PercentileRadar
          axes={axes}
          teamPercentiles={currentFractions}
          leaguePercentiles={baselineFractions.length ? baselineFractions : undefined}
          highlightOrder={highlightOrder}
          ringFractions={RING_FRACTIONS}
          ringLabels={RING_LABELS}
          baselinePercentile={0.5}
          showBaselineRing
          ringLabelOffsetY={0}
          legendItems={
            legendItems ?? [
              "Blue = current lineup",
              baselineFractions.length ? "Orange = baseline lineup" : "Orange baseline unavailable",
              "0 = league average; positive = above average (stronger)"
            ]
          }
        />
      ) : (
        !loading &&
        !error && <div className={styles.radarPlaceholder}>Add players to view radar.</div>
      )}
    </div>
  );
}
