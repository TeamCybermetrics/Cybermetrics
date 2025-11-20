import { PageCard } from "@/components";
import typography from "@/styles/typography.module.css";

export default function OurAlgorithmPage() {
  return (
    <PageCard title="Our Algorithm">
      <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
        <div>
          <h1 className={typography.heading1}>Our Algorithm</h1>
          <p className={typography.body}>
            Our algorithm is designed to help you quickly understand where your roster is strong, 
            where it needs support, and which players provide the most value relative to those needs. 
            To do that, we look at five batting stats: 
            strikeout rate (K%), walk rate (BB%), isolated power (ISO), on-base percentage (OBP), and base running (BsR).
          </p>
        </div>
        <div>
          <h1 className={typography.heading1}>Team Weakness Vectors</h1>
          <p className={typography.body}>
            Team weakness vectors show how your lineup compares to MLB averages. 
            For each stat, we calculate how far your team is from league average and express it as a z-score.
          </p>
        </div>
        <div>
          <h1 className={typography.heading1}>Adjustment Score</h1>
          <p className={typography.body}>
            The adjustment score shows how much a player helps or hurts your team in the areas where you're weakest. 
            After identifying your roster's gaps compared to MLB averages, we compare the player's recent stats to those 
            same league benchmarks and weight each difference by the size of the team weakness. A positive score means the 
            player strengthens the areas you need most, a negative score means they make those weaknesses worse.
          </p>
        </div>
        <div>
          <h1 className={typography.heading1}>Recommendation</h1>
          <p className={typography.body}>
            Our recommendation system begins by letting the manager choose which position they want to replace. 
            After calculating your team's current weakness vector relative to MLB averages, we evaluate every league 
            player at that same position. For each candidate, we simulate a hypothetical roster with that player swapped in, 
            recalculate the team weakness vector, and measure how much the total weakness decreases. The players who provide 
            the biggest improvement and most effectively reduce your team's gaps become our top recommendations.
          </p>
        </div>
      </div>
    </PageCard>
  );
}
