import math
from datetime import datetime
from typing import List, Dict
from entities.league_stats import TeamAggregate, LeagueAggregate


class LeagueStatsDomain:
    """helper logic for computing league aggregate statistics.

    """

    def compute_league_aggregate(self, teams: List[TeamAggregate]) -> LeagueAggregate:
        if not teams:
            raise ValueError("No teams provided for league aggregation")

        included = [t for t in teams if t.avg]
        if not included:
            raise ValueError("No team averages available to compute league aggregates")

        stat_keys = list(included[0].avg.keys())
        num_teams = len(included)
        total_players = sum(t.player_count for t in included)

        unweighted: Dict[str, float] = {}
        for k in stat_keys:
            s = sum(t.avg.get(k, 0.0) for t in included)
            unweighted[k] = round(s / num_teams, 4)

        if total_players > 0:
            weighted: Dict[str, float] = {}
            for k in stat_keys:
                s = sum(t.avg.get(k, 0.0) * t.player_count for t in included)
                weighted[k] = round(s / total_players, 4)
        else:
            weighted = dict(unweighted)

        unweighted_std: Dict[str, float] = {}
        for k in stat_keys:
            vals = [t.avg.get(k, 0.0) for t in included]
            mean_u = unweighted[k]
            var_u = sum((v - mean_u) ** 2 for v in vals) / len(vals)
            unweighted_std[k] = round(math.sqrt(var_u), 4)

        weighted_std: Dict[str, float] = {}
        if total_players > 0:
            for k in stat_keys:
                vals = [t.avg.get(k, 0.0) for t in included]
                weights = [t.player_count for t in included]
                mean_w = weighted[k]
                var_w_num = sum(w * (v - mean_w) ** 2 for v, w in zip(vals, weights))
                var_w = var_w_num / total_players
                weighted_std[k] = round(math.sqrt(var_w), 4)
        else:
            weighted_std = dict(unweighted_std)

        return LeagueAggregate(
            unweighted=unweighted,
            weighted_by_player_count=weighted,
            unweighted_std=unweighted_std,
            weighted_by_player_count_std=weighted_std,
            teams_counted=num_teams,
            players_counted=total_players,
            updated_at=datetime.utcnow().isoformat() + "Z",
        )
