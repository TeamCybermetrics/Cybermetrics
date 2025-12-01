from __future__ import annotations

def manual_contrib(player_stats, league_avg, league_std, team_weakness):
    """
    Compute per-key contribution scores and an overall contribution by comparing player statistics to league averages, scaled by league standard deviation and weighted by team weakness.
    
    Parameters:
        player_stats (dict): Mapping of metric name to player's value. Missing metrics are treated as 0.0.
        league_avg (dict): Mapping of metric name to league average. Missing metrics are treated as 0.0.
        league_std (dict): Mapping of metric name to league standard deviation. Missing metrics default to 100000.0.
        team_weakness (dict): Mapping of metric name to a weight; the absolute value is used. Missing metrics are treated as 0.0.
    
    Returns:
        tuple:
            total (float): Sum of all per-key contributions.
            result (dict): Mapping from metric name to its contribution, where contribution = (difference / std) * abs(weight).
                For "strikeout_rate" the difference is (league_avg - player_stats); for all other metrics it is (player_stats - league_avg).
    
    Raises:
        ZeroDivisionError: If any provided standard deviation in `league_std` is zero.
    """
    keys_lower_better = {"strikeout_rate"}
    result = {}
    total = 0.0
    for k in set(player_stats.keys()) | set(league_avg.keys()):
        p = float(player_stats.get(k, 0.0) or 0.0)
        l = float(league_avg.get(k, 0.0) or 0.0)
        std = float(league_std.get(k, 10**5) or 10**5)
        w = float(team_weakness.get(k, 0.0) or 0.0)
        diff = (l - p) if k in keys_lower_better else (p - l)
        contrib = diff / std * abs(w)
        result[k] = contrib
        total += contrib
    return total, result