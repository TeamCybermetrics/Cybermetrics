from fastapi import HTTPException, status
from entities.players import PlayerAvgStats, RosterAvgResponse
from typing import Dict, List, Optional


class RosterDomain:
    def __init__(self):
        pass

    def validate_player_ids(self, player_ids: List[int]) -> None:
        """Validate player IDs input"""
        if not player_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player IDs list cannot be empty",
            )

    def calculate_player_averages(self, seasons: Dict) -> Optional[PlayerAvgStats]:
        """Calculate career averages for a single player"""
        if not seasons:
            return None
        total_strikeout_rate = 0.0
        total_walk_rate = 0.0
        total_isolated_power = 0.0
        total_on_base_percentage = 0.0
        total_base_running = 0.0
        season_count = 0

        for _year, stats in seasons.items():
            # Only count seasons with plate appearances
            if stats.get("plate_appearances", 0) > 0:
                total_strikeout_rate += stats.get("strikeout_rate", 0.0)
                total_walk_rate += stats.get("walk_rate", 0.0)
                total_isolated_power += stats.get("isolated_power", 0.0)
                total_on_base_percentage += stats.get("on_base_percentage", 0.0)
                total_base_running += stats.get("base_running", 0.0)
                season_count += 1

        if season_count > 0:
            avg_strikeout_rate = round(total_strikeout_rate / season_count, 3)
            avg_walk_rate = round(total_walk_rate / season_count, 3)
            avg_isolated_power = round(total_isolated_power / season_count, 3)
            avg_on_base_percentage = round(total_on_base_percentage / season_count, 3)
            avg_base_running = round(total_base_running / season_count, 3)

            return PlayerAvgStats(
                strikeout_rate=avg_strikeout_rate,
                walk_rate=avg_walk_rate,
                isolated_power=avg_isolated_power,
                on_base_percentage=avg_on_base_percentage,
                base_running=avg_base_running,
            )

        return None

    def calculate_roster_averages(self, players_data: Dict[int, Dict]) -> RosterAvgResponse:
        """Calculate averages for entire roster"""
        stats_dict: Dict[int, PlayerAvgStats] = {}
        for player_id, season_stats in players_data.items():
            player_averages = self.calculate_player_averages(season_stats)
            if player_averages is not None:
                stats_dict[player_id] = player_averages
        return RosterAvgResponse(stats=stats_dict, total_players=len(stats_dict))

    def compute_unweighted_roster_average_dict(self, players_stats: List[PlayerAvgStats]) -> Dict[str, float]:
        """Compute an unweighted average across a list of PlayerAvgStats and return a plain dict.

        Raises HTTP 400 if the input list is empty.
        """
        if not players_stats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No player statistics provided to average",
            )

        total_k = 0.0
        total_bb = 0.0
        total_iso = 0.0
        total_obp = 0.0
        total_bsr = 0.0

        count = 0
        for s in players_stats:
            if s is None:
                continue
            total_k += getattr(s, "strikeout_rate", 0.0) or 0.0
            total_bb += getattr(s, "walk_rate", 0.0) or 0.0
            total_iso += getattr(s, "isolated_power", 0.0) or 0.0
            total_obp += getattr(s, "on_base_percentage", 0.0) or 0.0
            total_bsr += getattr(s, "base_running", 0.0) or 0.0
            count += 1

        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid player statistics to average",
            )

        return {
            "strikeout_rate": round(total_k / count, 3),
            "walk_rate": round(total_bb / count, 3),
            "isolated_power": round(total_iso / count, 3),
            "on_base_percentage": round(total_obp / count, 3),
            "base_running": round(total_bsr / count, 3),
        }

    def compute_team_weakness_scores(
        self, team_avg: Dict[str, float], league_avg: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute normalized weakness scores per stat vs league average.

        Definition (hitter context): higher score = more weakness (worse vs league).
        - For K% (lower is better): weakness_raw = max(0, team - league)
        - For BB%, ISO, OBP, BsR (higher is better): weakness_raw = max(0, league - team)
        Normalization: weakness_norm = weakness_raw / max(league, 1e-9)
        """
        keys_higher_better = {
            "walk_rate",
            "isolated_power",
            "on_base_percentage",
            "base_running",
        }
        keys_lower_better = {"strikeout_rate"}

        scores: Dict[str, float] = {}
        for key in keys_lower_better.union(keys_higher_better):
            team = float(team_avg.get(key, 0.0) or 0.0)
            league = float(league_avg.get(key, 0.0) or 0.0)

            if key in keys_lower_better:
                raw = max(0.0, team - league)
            else:  # higher is better
                raw = max(0.0, league - team)

            denom = league if league != 0 else 1e-9
            scores[key] = round(raw / denom, 3)

        return scores

    def calculate_player_latest_war(self, seasons: Dict) -> Optional[float]:
        """Return the player's latest season WAR (for the most recent season with PA > 0)."""
        if not seasons:
            return None
        try:
            ordered_years = sorted((int(y) for y in seasons.keys()), reverse=True)
        except Exception:
            ordered_years = list(seasons.keys())[::-1]

        for y in ordered_years:
            key = str(y)
            stats = seasons.get(key) or {}
            if (stats.get("plate_appearances", 0) or 0) > 0:
                return round(float(stats.get("war", 0.0) or 0.0), 3)
        return None

    def get_player_latest_stats(self, seasons: Dict) -> Optional[Dict[str, float]]:
        """Return the player's latest season stat snapshot for the 5 key metrics."""
        if not seasons:
            return None
        try:
            ordered_years = sorted((int(y) for y in seasons.keys()), reverse=True)
        except Exception:
            ordered_years = list(seasons.keys())[::-1]

        for y in ordered_years:
            key = str(y)
            s = seasons.get(key) or {}
            if (s.get("plate_appearances", 0) or 0) > 0:
                return {
                    "strikeout_rate": float(s.get("strikeout_rate", 0.0) or 0.0),
                    "walk_rate": float(s.get("walk_rate", 0.0) or 0.0),
                    "isolated_power": float(s.get("isolated_power", 0.0) or 0.0),
                    "on_base_percentage": float(s.get("on_base_percentage", 0.0) or 0.0),
                    "base_running": float(s.get("base_running", 0.0) or 0.0),
                }
        # Fallback to most recent season even if PA == 0
        key = str(ordered_years[0])
        s = seasons.get(key) or {}
        return {
            "strikeout_rate": float(s.get("strikeout_rate", 0.0) or 0.0),
            "walk_rate": float(s.get("walk_rate", 0.0) or 0.0),
            "isolated_power": float(s.get("isolated_power", 0.0) or 0.0),
            "on_base_percentage": float(s.get("on_base_percentage", 0.0) or 0.0),
            "base_running": float(s.get("base_running", 0.0) or 0.0),
        }

    def compute_value_score(
        self,
        latest_war: float,
        player_latest_stats: Dict[str, float],
        league_avg: Dict[str, float],
        team_weakness: Dict[str, float],
    ) -> Dict[str, float]:
        """Compute player value: latest WAR + team-weighted stat difference sum.

        For each stat s in {K%, BB%, ISO, OBP, BsR}:
          - If lower is better (K%): diff_s = league_s - player_s
          - Else (higher is better): diff_s = player_s - league_s
          - Contribution_s = diff_s * max(0, team_weakness_s)

        adjustment_score = sum(Contribution_s)
        value_score = latest_war + adjustment_score
        """
        if latest_war is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No player WAR available to compute value score",
            )
        if not player_latest_stats:
            player_latest_stats = {
                "strikeout_rate": 0.0,
                "walk_rate": 0.0,
                "isolated_power": 0.0,
                "on_base_percentage": 0.0,
                "base_running": 0.0,
            }

        keys_higher_better = {
            "walk_rate",
            "isolated_power",
            "on_base_percentage",
            "base_running",
        }
        keys_lower_better = {"strikeout_rate"}

        contributions: Dict[str, float] = {}
        adjustment_sum = 0.0
        for key in keys_lower_better.union(keys_higher_better):
            player_v = float(player_latest_stats.get(key, 0.0) or 0.0)
            league_v = float(league_avg.get(key, 0.0) or 0.0)
            weight = float(team_weakness.get(key, 0.0) or 0.0)
            if weight <= 0:
                continue  # ignore 0.0 weaknesses
            if key in keys_lower_better:
                diff = league_v - player_v  # lower is better
            else:
                diff = player_v - league_v  # higher is better
            contrib = diff * weight
            contributions[key] = round(contrib, 3)
            adjustment_sum += contrib

        adjustment_sum = round(adjustment_sum, 3)
        value_score = round(float(latest_war) + adjustment_sum, 3)
        return {
            "latest_war": round(float(latest_war), 3),
            "adjustment_score": adjustment_sum,
            "value_score": value_score,
            "contributions": contributions,
        }