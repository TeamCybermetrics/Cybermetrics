import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from server.config.firebase import firebase_service
from server.services.roster_avg_service import roster_avg_service
from server.utils.logger import setup_logger

logger = setup_logger(__name__)

async def compute_team_roster_average(team_doc_ref) -> Tuple[Dict[str, float], int]:
    """Compute roster averages for a single team document reference.

    Returns a dict with averaged stats (strikeout_rate, walk_rate, isolated_power,
    on_base_percentage, base_running) or empty dict if none could be computed.
    """
    try:
        team_snapshot = team_doc_ref.get()
        if not team_snapshot.exists:
            logger.warning(f"Team document {team_doc_ref.id} does not exist")
            return {}, 0

        team_data = team_snapshot.to_dict()
        positional_players = team_data.get("positional_players", [])
        if not positional_players:
            logger.info(f"No positional players for team {team_doc_ref.id}")
            return {}, 0

        # Extract mlbam ids from players
        player_ids: List[int] = []
        for p in positional_players:
            pid = p.get("mlbam_id")
            if pid:
                player_ids.append(int(pid))

        if not player_ids:
            logger.info(f"No mlbam_ids for team {team_doc_ref.id}")
            return {}, 0

        # Call the service (async)
        roster_response = await roster_avg_service.get_roster_averages(player_ids)

        stats_map = roster_response.stats or {}
        if not stats_map:
            logger.info(f"No stats returned for team {team_doc_ref.id}")
            return {}, 0

        # Compute averages across returned players
        sum_stats = {
            "strikeout_rate": 0.0,
            "walk_rate": 0.0,
            "isolated_power": 0.0,
            "on_base_percentage": 0.0,
            "base_running": 0.0,
        }
        count = 0
        for pid_str, stats in stats_map.items():
            # stats is a Pydantic model instance; access attributes
            try:
                sum_stats["strikeout_rate"] += float(stats.strikeout_rate)
                sum_stats["walk_rate"] += float(stats.walk_rate)
                sum_stats["isolated_power"] += float(stats.isolated_power)
                sum_stats["on_base_percentage"] += float(stats.on_base_percentage)
                sum_stats["base_running"] += float(stats.base_running)
                count += 1
            except Exception:
                logger.exception(f"Failed to read stats for player {pid_str} on team {team_doc_ref.id}")

        if count == 0:
            logger.info(f"No valid player stats to average for team {team_doc_ref.id}")
            return {}, 0

        avg_stats = {k: round(v / count, 4) for k, v in sum_stats.items()}
        return avg_stats, count

    except Exception as e:
        logger.exception(f"Error computing roster average for team {team_doc_ref.id}: {e}")
        return {}, 0


async def main():
    db = firebase_service.db
    if not db:
        logger.error("Firebase is not configured. Exiting.")
        return

    teams_ref = db.collection("teams")
    try:
        docs = teams_ref.stream()
    except Exception as e:
        logger.exception(f"Failed to stream teams collection: {e}")
        return

    # Collect per-team averages to later compute league aggregates
    team_averages: List[Dict[str, Any]] = []

    # Process each team sequentially (small number of teams)
    for doc in docs:
        team_id = doc.id
        logger.info(f"Processing team {team_id}...")
        team_ref = teams_ref.document(team_id)
        avg, player_count = await compute_team_roster_average(team_ref)
        if avg:
            try:
                # Save per-team roster_average as before
                team_ref.set({"roster_average": avg}, merge=True)
                logger.info(f"Saved roster_average for team {team_id}: {avg}")
            except Exception as e:
                logger.exception(f"Failed to save roster_average for team {team_id}: {e}")
            team_averages.append({"team_id": team_id, "avg": avg, "player_count": player_count})
        else:
            logger.info(f"No roster_average computed for team {team_id}")

    # After processing all teams, compute league-level aggregates
    try:
        included_teams = [t for t in team_averages if t.get("avg")]
        num_teams = len(included_teams)
        total_players = sum(t.get("player_count", 0) for t in included_teams)

        if num_teams == 0:
            logger.info("No team averages available to compute league averages.")
            return

        # Determine stat keys from first team's avg
        stat_keys = list(included_teams[0]["avg"].keys())

        # Unweighted average (mean across teams)
        unweighted = {}
        for k in stat_keys:
            s = sum(t["avg"].get(k, 0.0) for t in included_teams)
            unweighted[k] = round(s / num_teams, 4)

        # Weighted by player count average
        weighted = {}
        if total_players > 0:
            for k in stat_keys:
                s = sum(t["avg"].get(k, 0.0) * t.get("player_count", 0) for t in included_teams)
                weighted[k] = round(s / total_players, 4)
        else:
            # Fallback to unweighted if no player counts
            weighted = unweighted.copy()

        league_doc = {
            "unweighted": unweighted,
            "weighted_by_player_count": weighted,
            "teams_counted": num_teams,
            "players_counted": total_players,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        db.collection("league").document("averages").set(league_doc, merge=True)
        logger.info(f"Wrote league averages: teams={num_teams}, players={total_players}")

    except Exception as e:
        logger.exception(f"Failed to compute/write league averages: {e}")


if __name__ == "__main__":
    asyncio.run(main())
