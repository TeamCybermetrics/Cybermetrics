import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime

from repositories.player_repository import PlayerRepository
from services.roster_avg_service import RosterAvgService
from services.league_stats_service import LeagueStatsService
from useCaseHelpers.league_stats_helper import LeagueStatsDomain
from entities.league_stats import TeamAggregate
from utils.logger import setup_logger  # or get_logger if that's what you use

logger = setup_logger(__name__)

async def compute_team_roster_average(team_id: str, teams_repo: PlayerRepository, roster_service: RosterAvgService) -> Tuple[Dict[str, float], int]:
    """Compute roster averages for one team by its document id."""
    try:
        positional_players = teams_repo.get_team_positional_players(team_id) or []
        if not positional_players:
            logger.info(f"No positional players for team {team_id}")
            return {}, 0

        player_ids: List[int] = []
        for p in positional_players:
            pid = p.get("mlbam_id")
            if pid is not None:
                try:
                    player_ids.append(int(pid))
                except Exception:
                    continue

        if not player_ids:
            logger.info(f"No mlbam_ids for team {team_id}")
            return {}, 0

        roster_response = await roster_service.get_roster_averages(player_ids)
        stats_map = getattr(roster_response, "stats", None) or {}
        if not stats_map:
            logger.info(f"No stats returned for team {team_id}")
            return {}, 0

        sum_stats = {
            "strikeout_rate": 0.0,
            "walk_rate": 0.0,
            "isolated_power": 0.0,
            "on_base_percentage": 0.0,
            "base_running": 0.0,
        }
        count = 0

        for pid_str, stats in stats_map.items():
            try:
                # Support either Pydantic object or plain dict
                getv = (lambda k: getattr(stats, k)) if hasattr(stats, "__dict__") else (lambda k: stats.get(k))
                sum_stats["strikeout_rate"] += float(getv("strikeout_rate"))
                sum_stats["walk_rate"] += float(getv("walk_rate"))
                sum_stats["isolated_power"] += float(getv("isolated_power"))
                sum_stats["on_base_percentage"] += float(getv("on_base_percentage"))
                sum_stats["base_running"] += float(getv("base_running"))
                count += 1
            except Exception:
                logger.exception(f"Failed to read stats for player {pid_str} on team {team_id}")

        if count == 0:
            logger.info(f"No valid player stats to average for team {team_id}")
            return {}, 0

        avg_stats = {k: round(v / count, 4) for k, v in sum_stats.items()}
        return avg_stats, count

    except Exception as e:
        logger.exception(f"Error computing roster average for team {team_id}: {e}")
        return {}, 0


async def main(teams_repo: PlayerRepository, roster_service: RosterAvgService) -> None:
    """Compute per-team roster averages and league aggregates; write via TeamsRepository."""
    # Per-team averages
    team_aggregates: List[TeamAggregate] = []
    for team_id in teams_repo.list_team_ids():
        try:
            logger.info(f"Processing team {team_id}...")
            avg, player_count = await compute_team_roster_average(team_id, teams_repo, roster_service)
            if avg:
                try:
                    teams_repo.set_team_roster_average(team_id, avg)
                    logger.info(f"Saved roster_average for team {team_id}: {avg}")
                except Exception as e:
                    logger.exception(f"Failed to save roster_average for team {team_id}: {e}")
                team_aggregates.append(TeamAggregate(team_id=team_id, avg=avg, player_count=player_count))
            else:
                logger.info(f"No roster_average computed for team {team_id}")
        except Exception:
            logger.exception(f"Team processing failed: {team_id}")

    if not team_aggregates:
        logger.info("No team aggregates available to compute league averages.")
        return
    league_service = LeagueStatsService(player_repository=teams_repo, domain=LeagueStatsDomain())
    try:
        league_agg = league_service.compute_and_persist(team_aggregates)
        logger.info(
            "Wrote league averages: teams=%s players=%s", league_agg.teams_counted, league_agg.players_counted
        )
    except Exception as e:
        logger.exception(f"Failed to compute/write league averages: {e}")


if __name__ == "__main__":
    raise SystemExit("Use a runner or scheduler to inject TeamsRepository and RosterAvgService.")