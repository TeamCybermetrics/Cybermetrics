from __future__ import annotations

def manual_contrib(player_stats, league_avg, league_std, team_weakness):
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
