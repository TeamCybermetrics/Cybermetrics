"""
Factories for testing roster functions.
"""
from __future__ import annotations
import math
from typing import Dict, List
from repositories.roster_avg_repository import RosterRepository


def build_fake_players() -> Dict[int, Dict]:
    """Construct deterministic multi-season stats for several players.

    Each player includes per-season stat snapshots plus WAR. Plate appearances
    are used to select the latest valid season.
    """
    return {
        101: {
            "2023": {"plate_appearances": 500, "strikeout_rate": 0.21, "walk_rate": 0.09, "isolated_power": 0.165, "on_base_percentage": 0.345, "base_running": 1.1, "war": 4.8},
            "2022": {"plate_appearances": 480, "strikeout_rate": 0.22, "walk_rate": 0.08, "isolated_power": 0.160, "on_base_percentage": 0.340, "base_running": 1.0, "war": 4.2},
        },
        102: {
            "2023": {"plate_appearances": 510, "strikeout_rate": 0.24, "walk_rate": 0.07, "isolated_power": 0.155, "on_base_percentage": 0.330, "base_running": 0.8, "war": 3.1},
            "2022": {"plate_appearances": 300, "strikeout_rate": 0.25, "walk_rate": 0.06, "isolated_power": 0.150, "on_base_percentage": 0.325, "base_running": 0.7, "war": 2.5},
        },
        103: {
            "2023": {"plate_appearances": 520, "strikeout_rate": 0.19, "walk_rate": 0.10, "isolated_power": 0.180, "on_base_percentage": 0.355, "base_running": 1.3, "war": 5.2},
        },
        104: {
            "2023": {"plate_appearances": 470, "strikeout_rate": 0.23, "walk_rate": 0.11, "isolated_power": 0.175, "on_base_percentage": 0.350, "base_running": 1.0, "war": 4.5},
        },
    }


def _extract_latest_stats(seasons: Dict) -> Dict[str, float]:
    if not seasons:
        return {}
    ordered = sorted((int(y) for y in seasons.keys()), reverse=True)
    for y in ordered:
        s = seasons[str(y)]
        if (s.get("plate_appearances", 0) or 0) > 0:
            return {
                "strikeout_rate": float(s.get("strikeout_rate", 0.0) or 0.0),
                "walk_rate": float(s.get("walk_rate", 0.0) or 0.0),
                "isolated_power": float(s.get("isolated_power", 0.0) or 0.0),
                "on_base_percentage": float(s.get("on_base_percentage", 0.0) or 0.0),
                "base_running": float(s.get("base_running", 0.0) or 0.0),
            }
    return {}


def _average_dicts(dicts: List[Dict[str, float]]) -> Dict[str, float]:
    if not dicts:
        return {"strikeout_rate": 0, "walk_rate": 0, "isolated_power": 0, "on_base_percentage": 0, "base_running": 0}
    keys = dicts[0].keys()
    return {k: sum(d.get(k, 0.0) for d in dicts) / len(dicts) for k in keys}


def _std_dicts(dicts: List[Dict[str, float]]) -> Dict[str, float]:
    if not dicts:
        return {"strikeout_rate": 0, "walk_rate": 0, "isolated_power": 0, "on_base_percentage": 0, "base_running": 0}
    avg = _average_dicts(dicts)
    out: Dict[str, float] = {}
    keys = dicts[0].keys()
    for k in keys:
        vals = [d.get(k, 0.0) for d in dicts]
        mean = avg[k]
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        out[k] = math.sqrt(var) or 10**-9
    return out


async def fetch_league_vectors(repo: RosterRepository) -> tuple[Dict[str, float], Dict[str, float]]:
    """Return (league_avg, league_std) using repository accessors."""
    return await repo.get_league_unweighted_average(), await repo.get_league_unweighted_std()
