from __future__ import annotations

PLAYER_STATS = {
    "strikeout_rate": 0.22,
    "walk_rate": 0.09,
    "isolated_power": 0.170,
    "on_base_percentage": 0.340,
    "base_running": 1.2,
}

LEAGUE_AVG = {
    "strikeout_rate": 0.23,
    "walk_rate": 0.08,
    "isolated_power": 0.160,
    "on_base_percentage": 0.330,
    "base_running": 1.0,
}

LEAGUE_STD = {
    "strikeout_rate": 0.02,
    "walk_rate": 0.01,
    "isolated_power": 0.02,
    "on_base_percentage": 0.015,
    "base_running": 0.5,
}

TEAM_WEAKNESS_MIXED = {
    "strikeout_rate": 0.50,
    "walk_rate": -0.30,
    "isolated_power": -0.20,
    "on_base_percentage": 0.40,
    "base_running": 0.00,
}


def manual_contrib(player_stats, league_avg, league_std, team_weakness):
    """Compute expected contributions mirroring current domain logic (abs(weight))."""
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
