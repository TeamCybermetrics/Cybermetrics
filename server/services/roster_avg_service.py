from fastapi import HTTPException, status
from server.models.players import RosterAvgResponse, PlayerAvgStats, PlayerValueScore
from typing import List, Dict, Optional
from server.repositories.roster_avg_repository import RosterRepository
from server.domain.roster_domain import RosterDomain
from server.repositories.player_repository import PlayerRepository
import logging

logger = logging.getLogger(__name__)

class RosterAvgService:
    """Service for calculating roster average statistics"""
    
    def __init__(self, roster_repository: RosterRepository, roster_domain: RosterDomain, player_repository: PlayerRepository):
        self.roster_repository = roster_repository
        self.roster_domain = roster_domain
        self.player_repository = player_repository
    
    async def get_roster_averages(self, player_ids: List[int]) -> RosterAvgResponse:
        """
        Get average stats for a list of player IDs.
        
        Calculates career averages across all seasons for:
        - Strikeout rate (K%)
        - Walk rate (BB%)
        - Isolated power (ISO)
        - On-base percentage (OBP)
        - Base running value (BsR)
        
        Args:
            player_ids: List of MLB player IDs (mlbam_id)
            
        Returns:
            RosterAvgResponse with stats for each player
        """
        self.roster_domain.validate_player_ids(player_ids)

        players_data = await self.roster_repository.get_players_seasons_data(player_ids)

        averages = self.roster_domain.calculate_roster_averages(players_data)

        return averages

    async def get_unweighted_roster_average(self, player_ids: List[int]) -> Dict[str, float]:
        """Compute and return the unweighted average of roster stats as a plain dictionary.

        This orchestrates the workflow:
        - validate inputs (domain)
        - load players' season data (repository)
        - compute per-player averages (domain)
        - compute unweighted roster aggregate (domain)

        Args:
            player_ids: List of MLB player IDs (mlbam_id)

        Returns:
            Dict with keys: strikeout_rate, walk_rate, isolated_power, on_base_percentage, base_running
        """
        self.roster_domain.validate_player_ids(player_ids)

        players_data = await self.roster_repository.get_players_seasons_data(player_ids)
        roster_response = self.roster_domain.calculate_roster_averages(players_data)
        # Aggregate across players into a plain dict
        return self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

    async def get_team_weakness_scores(self, player_ids: List[int]) -> Dict[str, float]:
        """Rank each stat as a team weakness vs league unweighted average.

        Higher value => more weakness relative to league. Values are normalized by
        league average per-stat so scores are unitless.
        """
        self.roster_domain.validate_player_ids(player_ids)

        # Compute team unweighted average
        players_data = await self.roster_repository.get_players_seasons_data(player_ids)
        roster_response = self.roster_domain.calculate_roster_averages(players_data)
        team_avg = self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

        # Fetch league unweighted average
        league_avg = await self.roster_repository.get_league_unweighted_average()

        # Compute normalized weakness scores
        return self.roster_domain.compute_team_weakness_scores(team_avg, league_avg)

    async def get_value_score(self, player_id: int, team_weakness_scores: Dict[str, float]) -> Dict[str, float]:
        """Compute a value score: latest WAR adjusted by team-weighted stat differences.

        Steps:
        - Load player's seasons
        - Extract latest WAR and latest season's key stats
        - Fetch league unweighted averages
        - Compute per-stat (direction-aware) differences and weight by team weaknesses (ignore 0.0)
        - Sum contributions and add to latest WAR
        """
        players_data = await self.roster_repository.get_players_seasons_data([player_id])
        seasons = players_data.get(player_id)
        if seasons is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player {player_id} not found or has no season data",
            )

        latest_war = self.roster_domain.calculate_player_latest_war(seasons)
        latest_stats = self.roster_domain.get_player_latest_stats(seasons) or {}
        league_avg = await self.roster_repository.get_league_unweighted_average()

        return self.roster_domain.compute_value_score(
            latest_war=latest_war,
            player_latest_stats=latest_stats,
            league_avg=league_avg,
            team_weakness=team_weakness_scores,
        )

    async def get_team_value_scores(self, player_ids: List[int]) -> List[PlayerValueScore]:
        """Compute team weakness from the given players and return each player's id, name, and value_score."""
        self.roster_domain.validate_player_ids(player_ids)

        # Compute team weakness once for the provided roster
        weakness = await self.get_team_weakness_scores(player_ids)

        results: List[PlayerValueScore] = []
        for pid in player_ids:
            try:
                # Compute value score for each player
                vs = await self.get_value_score(pid, weakness)
                # Fetch player name (skip if missing)
                pdata = await self.player_repository.get_player_by_id(pid)
                if not pdata:
                    continue
                name = pdata.get("name", "Unknown")
                results.append(
                    PlayerValueScore(
                        id=pid,
                        name=name,
                        adjustment_score=vs.get("adjustment_score", 0.0),
                        value_score=vs.get("value_score", 0.0),
                    )
                )
            except HTTPException as e:
                if e.status_code < 500:
                    continue
                else:
                    raise
            except Exception:
                logger.exception("Unexpected error computing value score for player %s", pid)
                # For any unexpected error with a single player, skip and continue
                continue

        return results



