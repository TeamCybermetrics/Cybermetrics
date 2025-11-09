"""Service layer for lineup-based player recommendations."""

from typing import List, Dict, Optional

from fastapi import HTTPException, status
from models.players import PlayerSearchResult
from repositories.roster_avg_repository import RosterRepository
from domain.roster_domain import RosterDomain
from repositories.player_repository import PlayerRepository
from domain.player_domain import PlayerDomain
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Coordinates domain logic and data access for recommendations."""

    def __init__(
        self,
        roster_repository: RosterRepository,
        roster_domain: RosterDomain,
        player_repository: PlayerRepository,
        player_domain: Optional[PlayerDomain] = None,
    ):
        self.roster_repository = roster_repository
        self.roster_domain = roster_domain
        self.player_repository = player_repository
        self.player_domain = player_domain or PlayerDomain()

    async def recommend_players(self, player_ids: List[int]) -> List[PlayerSearchResult]:
        """
        Return 5 recommmended players for there rooster based off of the 
        1. Get current team weakness vector (weakness_s) → where each stat's value > 0 means 
        team underperforms the league average. 
        
        2. Find the player iwth the lowest adjustment score, this is the 
        player we will replcae and there positions 
        
        3. Fetch all free agents from firebase (there mlbid) 
        
        4. for each team hypothetiically create a ne weakness vector with this player instead of the replaced player 
        
        5. Store the player id with the difference between the sum of old weakness vector - new weakness vector 
        
        6. Return the top 5 mlbid with the higest difference (maybe in a hashmap with mlbid, and the difference)
        
        Placeholder orchestration method for future recommendation flow."""

        # 1. Get current team weakness vector (weakness_s) where each stat's value > 0 means team underperforms the league average. 
        self.roster_domain.validate_player_ids(player_ids)

        # Compute team unweighted average
        players_data = await self.roster_repository.get_players_seasons_data(player_ids)
        roster_response = self.roster_domain.calculate_roster_averages(players_data)
        team_avg = self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

        # Fetch league unweighted average
        league_avg = await self.roster_repository.get_league_unweighted_average()

        # Compute normalized weakness scores
        original_weakness_vector = self.roster_domain.compute_team_weakness_scores(team_avg, league_avg)


        # 2. find the player with lowest adjustment sore
        original_players_adjustment_scores: Dict[int, float] = {}
        player_seasons_map: Dict[int, Dict] = {}
        for player_id in player_ids:

            players_data = await self.roster_repository.get_players_seasons_data([player_id])
            seasons = players_data.get(player_id)
            if seasons is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player {player_id} not found or has no season data",
                )

            latest_stats = self.roster_domain.get_player_latest_stats(seasons) or {}
            league_avg = await self.roster_repository.get_league_unweighted_average()

            original_players_adjustment_scores[player_id] = self.roster_domain.compute_adjustment_war(
                player_latest_stats=latest_stats,
                league_avg=league_avg,
                team_weakness=original_weakness_vector,
            )
            player_seasons_map[player_id] = seasons

        if not original_players_adjustment_scores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to compute adjustment scores for roster",
            )

        min_adjustment_score_player_id = min(
            original_players_adjustment_scores, key=original_players_adjustment_scores.get
        )

        replaced_player_data = await self.player_repository.get_player_by_id(min_adjustment_score_player_id)
        primary_position = self.player_domain.get_primary_position(
            replaced_player_data or {},
            player_seasons_map.get(min_adjustment_score_player_id),
        )

        if not primary_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to determine position for player {min_adjustment_score_player_id}",
            )

        # 3. Fetch all free agents from firebase (there mlbid) 
        free_agents_list = await self.roster_repository.get_free_agents()
        primary_position_upper = primary_position.upper()
        free_agents_list = [
            agent
            for agent in free_agents_list
            if str(agent.get("position") or "").strip().upper() == primary_position_upper
        ]

        if not free_agents_list:
            self._logger.info(
                "No free agents found for position %s; returning empty recommendations",
                primary_position_upper,
            )
            return []

        free_agents_contributions = {} # dictionary of key is mlbam_id and value is the difference between the sum of original weakness vector
        # and sum of this vector
        original_vector_sum = sum(original_weakness_vector.values())

        # 4. for each team hypothetiically create a ne weakness vector with this player instead of the replaced player  
        for player in free_agents_list:
            free_agent_player_id = player.get("mlbam_id")
            if not isinstance(free_agent_player_id, int):
                continue

            candidate_player_ids = [
                pid for pid in player_ids if pid != min_adjustment_score_player_id
            ]
            candidate_player_ids.append(free_agent_player_id)

            self.roster_domain.validate_player_ids(candidate_player_ids)

            # Compute team unweighted average
            players_data = await self.roster_repository.get_players_seasons_data(candidate_player_ids)
            roster_response = self.roster_domain.calculate_roster_averages(players_data)
            team_avg = self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

            # Fetch league unweighted average
            league_avg = await self.roster_repository.get_league_unweighted_average()

            # Compute normalized weakness scores
            potential_team_weakness_vector = self.roster_domain.compute_team_weakness_scores(team_avg, league_avg)

            # 5. Store the player id with the difference between the sum of old weakness vector - new weakness vector 
            free_agents_contributions[free_agent_player_id] = original_vector_sum - sum(potential_team_weakness_vector.values())
        
        top_5_id_and_score = sorted(free_agents_contributions.items(), key=lambda x: x[1], reverse=True)[:5]
        results: List[PlayerSearchResult] = []
        for mlbam_id, contribution in top_5_id_and_score:
            player_data = await self.player_repository.get_player_by_id(mlbam_id)
            if not player_data:
                continue

            player_result = self.player_domain._build_player_search_result(player_data, contribution)
            if player_result:
                results.append(player_result)

        return results