import type { PanelMode } from "./useRecommendations";
import styles from "./RecommendationsView.module.css";

type Props = {
  mode: PanelMode;
  query: string;
  onGetRecommendations: () => void;
  onSearchChange: (value: string) => void;
  onSaveLineup: () => void;
};

export function RecommendationsView({
  mode,
  query,
  onGetRecommendations,
  onSearchChange,
  onSaveLineup,
}: Props) {
  return (
    <div className={styles.layout}>
      {/* Left column */}
      <div className={styles.leftCol}>
        {/* Team Weakness box at top */}
        <div className={styles.weaknessCard}>
          <div className={styles.weaknessTitle}>Changes in Team Weakness</div>
          <div className={styles.weaknessGrid}>
            <div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreGreen}>Score +01</div>
            </div>
            <div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
              <div className={styles.weakLabel}>Strikeout Rate</div>
              <div className={styles.weakScoreRed}>Score -01</div>
            </div>
          </div>
        </div>

        {/* Get Recommendations button */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>Click to get recommendations</div>
          <button className={styles.ctaBtn} onClick={onGetRecommendations}>
            Get Recommendations!
          </button>
        </div>

        {/* Search bar */}
        <div className={styles.card}>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search players by name, team, or position..."
            aria-label="Search players by name, team, or position"
            value={query}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          <div className={styles.savedHint}>9 saved players</div>
        </div>

        {/* Unified output panel for both search and recommendations */}
        <div className={styles.displayPanel}>
          {mode === "idle" && (
            <div className={styles.placeholder}>
              Use the search bar or click "Get Recommendations!" to see results here.
            </div>
          )}
          {mode === "recommendations" && (
            <div className={styles.placeholder}>
              {/* TODO: <RecommendationsSection ... /> */}
              Recommendations will appear here.
            </div>
          )}
          {mode === "search" && (
            <div className={styles.placeholder}>
              {/* TODO: <SearchResultsSection query={query} ... /> */}
              Results for "{query}" will appear here.
            </div>
          )}
        </div>
      </div>

      {/* Right column */}
      <div className={styles.rightCol}>
        {/* Before/After Radar at top */}
        <div className={styles.radarCard}>
          <div className={styles.radarHeader}>Before/After</div>
          <div className={styles.radarSubheader}>Weakness radar</div>
          {/* TODO: <BeforeAfterRadar ... /> */}
          <div className={styles.radarPlaceholder} />
        </div>

        {/* Diamond panel below radar */}
        <div className={styles.diamondCard}>
          <div className={styles.diamondHeader}>
            <div>Your lineup</div>
            <div className={styles.activeBadge}>ACTIVE: CF</div>
          </div>
          <div className={styles.diamondCanvas}>
            {/* TODO: <DiamondPanel ... /> */}
            <div className={styles.diamondPlaceholder}>Diamond UI</div>
          </div>
          <div className={styles.diamondFooter}>
            <button className={styles.saveBtn} onClick={onSaveLineup}>
              Save Lineup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}