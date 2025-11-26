"""Service layer for lineup-based player recommendations."""

from typing import List, Dict, Optional

import logging
import time

from dtos.player_dtos import PlayerSearchResult
from repositories.roster_avg_repository import RosterRepository
from useCaseHelpers.roster_helper import RosterDomain
from repositories.player_repository import PlayerRepository
from useCaseHelpers.player_helper import PlayerDomain
from useCaseHelpers.errors import InputValidationError, QueryError


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
        
        3. Fetch all players from firebase (there mlbid) whose position matches with what we need
        
        4. for each team hypothetiically create a ne weakness vector with this player instead of the replaced player 
        
        5. Store the player id with the difference between the sum of old weakness vector - new weakness vector 
        
        6. Return the top 5 mlbid with the higest difference (maybe in a hashmap with mlbid, and the difference)
        
        Placeholder orchestration method for future recommendation flow."""

        if len(player_ids) < 9:
            raise InputValidationError("A valid roster must contain at least 9 players.")

        start_time = time.perf_counter()

        # 1. Get current team weakness vector (weakness_s) where each stat's value > 0 means team underperforms the league average. 
        self.roster_domain.validate_player_ids(player_ids)

        # Compute team unweighted average
        roster_players_data = await self.roster_repository.get_players_seasons_data(player_ids)
        roster_response = self.roster_domain.calculate_roster_averages(roster_players_data)
        team_avg = self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

        # Fetch league unweighted average
        league_avg = await self.roster_repository.get_league_unweighted_average()
        league_std = await self.roster_repository.get_league_unweighted_std()

        # Compute normalized weakness scores
        original_weakness_vector = self.roster_domain.compute_team_weakness_scores(team_avg, league_avg, league_std)


        # 2. find the player with lowest adjustment sore
        original_players_adjustment_scores: Dict[int, float] = {}
        player_seasons_map: Dict[int, Dict] = {}
        for player_id in player_ids:

            seasons = roster_players_data.get(player_id)
            if seasons is None:
                raise QueryError(f"Player {player_id} has no season data, could not give recommendations")

            latest_stats = self.roster_domain.get_player_latest_stats(seasons) or {}

            original_players_adjustment_scores[player_id] = self.roster_domain.compute_adjustment_sum(
                player_latest_stats=latest_stats,
                league_avg=league_avg,
                league_std=league_std,
                team_weakness=original_weakness_vector,
            )[0]
            player_seasons_map[player_id] = seasons

        min_adjustment_score_player_id = min(
            original_players_adjustment_scores, key=original_players_adjustment_scores.get
        )

        replaced_player_data = await self.player_repository.get_player_by_id(min_adjustment_score_player_id)
        primary_position = self.player_domain.get_primary_position(
            replaced_player_data or {},
            player_seasons_map.get(min_adjustment_score_player_id),
        )

        if not primary_position:
            raise InputValidationError(
                f"Unable to determine position for player {min_adjustment_score_player_id}"
            )

        # 3. Fetch all players and filter by target position
        all_players = await self.player_repository.get_all_players()
        primary_position_upper = primary_position.upper()
        position_matched_players = [
            player
            for player in all_players
            if str(player.get("position") or "").strip().upper() == primary_position_upper
        ]

        player_contributions = {}  # dictionary of key is mlbam_id and value is the difference between the sum of original weakness vector
        # and sum of this vector
        original_vector_sum = sum(original_weakness_vector.values())

        # 4. for each team hypothetiically create a ne weakness vector with this player instead of the replaced player  
        base_roster_without_replaced = {
            pid: roster_players_data[pid]
            for pid in player_ids
            if pid != min_adjustment_score_player_id
        }
        candidate_seasons_cache: Dict[int, Dict] = {}

        for player in position_matched_players:
            candidate_player_id = player.get("mlbam_id")
            if not isinstance(candidate_player_id, int):
                continue

            candidate_seasons = candidate_seasons_cache.get(candidate_player_id)
            if candidate_seasons is None:
                candidate_data_map = await self.roster_repository.get_players_seasons_data([candidate_player_id])
                candidate_seasons = candidate_data_map.get(candidate_player_id)
                if not candidate_seasons:
                    continue
                candidate_seasons_cache[candidate_player_id] = candidate_seasons

            candidate_players_data = dict(base_roster_without_replaced)
            candidate_players_data[candidate_player_id] = candidate_seasons

            # Compute team unweighted average for the hypothetical roster
            roster_response = self.roster_domain.calculate_roster_averages(candidate_players_data)
            team_avg = self.roster_domain.compute_unweighted_roster_average_dict(list(roster_response.stats.values()))

            # Compute normalized weakness scores
            potential_team_weakness_vector = self.roster_domain.compute_team_weakness_scores(team_avg, league_avg, league_std)

            # 5. Store the player id with the difference between the sum of old weakness vector - new weakness vector 
            player_contributions[candidate_player_id] = original_vector_sum - sum(potential_team_weakness_vector.values())

        top_5_id_and_score = sorted(player_contributions.items(), key=lambda x: x[1], reverse=False)[:5]
        results: List[PlayerSearchResult] = []
        for mlbam_id, contribution in top_5_id_and_score:
            player_data = await self.player_repository.get_player_by_id(mlbam_id)

            player_result = self.player_domain.build_player_search_result(
                player_data,
                contribution,
                self.player_repository.build_player_image_url,
            )
            if player_result:
                results.append(player_result)

        return results

        