from typing import Dict, List, Optional, Callable
from dtos.roster_dtos import RosterAvgResponse, PlayerAvgStats
from dtos.player_dtos import PlayerSearchResult
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.player_helper import PlayerDomain
from useCaseHelpers.errors import InputValidationError


class MockRosterHelper(RosterDomain):
    """Mock roster use case helper for tests """
    def __init__(self):
        # private attirbutes for testing
        self._should_raise_validation_error = False
        self._validation_error_message = "Player IDs list cannot be empty"
        self._roster_response: Optional[RosterAvgResponse] = None
        self._team_avg: Optional[Dict[str, float]] = None
        self._weakness_vector: Optional[Dict[str, float]] = None
        self._latest_stats: Optional[Dict[str, float]] = None
        self._adjustment_sum: float = 0.0
        self._adjustment_contributions: Dict[str, float] = {}
    
    def validate_player_ids(self, player_ids: List[int]) -> None:
        """validates player ids"""
        if self._should_raise_validation_error:
            raise InputValidationError(self._validation_error_message)
        if not player_ids:
            raise InputValidationError("Player IDs list cannot be empty")
    
    def calculate_roster_averages(self, players_data: Dict[int, Dict]) -> RosterAvgResponse:
        """calc roster averages"""
        if self._roster_response is not None:
            return self._roster_response
        
        # default response 
        stats = {}
        for player_id in players_data.keys():
            stats[player_id] = PlayerAvgStats(
                strikeout_rate=0.20,
                walk_rate=0.08,
                isolated_power=0.15,
                on_base_percentage=0.32,
                base_running=0.0
            )
        return RosterAvgResponse(stats=stats, total_players=len(stats))
    
    def compute_unweighted_roster_average_dict(self, players_stats: List[PlayerAvgStats]) -> Dict[str, float]:
        """compute unweighted avg"""
        if self._team_avg is not None:
            return self._team_avg.copy()
        
        # default stats
        return {
            "strikeout_rate": 0.20,
            "walk_rate": 0.08,
            "isolated_power": 0.15,
            "on_base_percentage": 0.32,
            "base_running": 0.0
        }
    
    def compute_team_weakness_scores(
        self, team_avg: Dict[str, float], league_avg: Dict[str, float], league_std: Dict[str, float]
    ) -> Dict[str, float]:
        """compute weakness scores"""
        if self._weakness_vector is not None:
            return self._weakness_vector.copy()
        
        # default weakness values
        return {
            "strikeout_rate": 0.5,
            "walk_rate": -0.3,
            "isolated_power": -0.2,
            "on_base_percentage": -0.1,
            "base_running": 0.0
        }
    
    def get_player_latest_stats(self, seasons: Dict) -> Optional[Dict[str, float]]:
        """get latest stats for player"""
        if self._latest_stats is not None:
            return self._latest_stats.copy()
        
        # default stats
        return {
            "strikeout_rate": 0.20,
            "walk_rate": 0.08,
            "isolated_power": 0.15,
            "on_base_percentage": 0.32,
            "base_running": 0.0
        }
    
    def compute_adjustment_sum(
        self,
        player_latest_stats: Dict[str, float],
        league_avg: Dict[str, float],
        league_std: Dict[str, float],
        team_weakness: Dict[str, float],
    ) -> tuple[float, Dict[str, float]]:
        """compute adjustment"""
        return (self._adjustment_sum, self._adjustment_contributions.copy())

    # helper function to set up mock helpers for the rooster
    def set_validation_error(self, should_raise: bool, message: str = "Player IDs list cannot be empty"):
        """set if validation should error"""
        self._should_raise_validation_error = should_raise
        self._validation_error_message = message
    
    def set_roster_response(self, response: RosterAvgResponse):
        """set what roster response to return"""
        self._roster_response = response
    
    def set_team_avg(self, team_avg: Dict[str, float]):
        """set team avg"""
        self._team_avg = team_avg.copy()
    
    def set_weakness_vector(self, weakness: Dict[str, float]):
        """set weakness vector"""
        self._weakness_vector = weakness.copy()
    
    def set_latest_stats(self, stats: Optional[Dict[str, float]]):
        """set latest stats"""
        self._latest_stats = stats.copy() if stats is not None else None
    
    def set_adjustment_sum(self, adjustment_sum: float, contributions: Optional[Dict[str, float]] = None):
        """set adjustment sum"""
        self._adjustment_sum = adjustment_sum
        self._adjustment_contributions = contributions or {}
    
    def reset(self):
        """reset everything back to defaults"""
        self._should_raise_validation_error = False
        self._validation_error_message = "Player IDs list cannot be empty"
        self._roster_response = None
        self._team_avg = None
        self._weakness_vector = None
        self._latest_stats = None
        self._adjustment_sum = 0.0
        self._adjustment_contributions = {}

class MockPlayerHelper(PlayerDomain):
    """Mock player use case helper for tests"""
    def __init__(self):
        self._primary_position: Optional[str] = "RF"
        self._should_return_none_position = False
        self._search_result: Optional[PlayerSearchResult] = None
        self._should_return_none_result = False
    
    def get_primary_position(self, player_data: Dict, seasons: Optional[Dict] = None) -> Optional[str]:
        """get primary position"""
        if self._should_return_none_position:
            return None
        return self._primary_position
    
    def build_player_search_result(self, player: Dict, score: float, image_builder: Optional[Callable[[int], str]] = None,) -> Optional[PlayerSearchResult]:
        """build player search result"""
        if self._should_return_none_result:
            return None
        
        if self._search_result is not None:
            return self._search_result
        
        # build from player data
        mlbam_id = player.get("mlbam_id")
        if not isinstance(mlbam_id, int) or mlbam_id <= 0:
            return None
        
        builder = image_builder or (lambda _: "")
        seasons = player.get("seasons", {})
        
        # calc years active
        if seasons:
            years = sorted([int(y) for y in seasons.keys() if str(y).isdigit()])
            if years:
                first_year = str(years[0])
                last_year = str(years[-1])
                years_active = first_year if first_year == last_year else f"{first_year}-{last_year}"
            else:
                years_active = "Unknown"
        else:
            years_active = "Unknown"
        
        return PlayerSearchResult(
            id=mlbam_id,
            name=player.get("name", ""),
            score=score,
            image_url=builder(mlbam_id),
            years_active=years_active
        )
    
    # test case helpers here to mock unexpected behaviours
    
    def set_primary_position(self, position: Optional[str]):
        """set primary position"""
        self._primary_position = position
        self._should_return_none_position = (position is None)
    
    def set_search_result(self, result: Optional[PlayerSearchResult]):
        """set search result to return"""
        self._search_result = result
        self._should_return_none_result = (result is None)
    
    def reset(self):
        """reset to defaults"""
        self._primary_position = "RF"
        self._should_return_none_position = False
        self._search_result = None
        self._should_return_none_result = False

