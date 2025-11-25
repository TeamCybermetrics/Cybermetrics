import pytest
from typing import Dict
from services.recommendation_service import RecommendationService
from useCaseHelpers.errors import InputValidationError
from services.tests.mocks.mock_repositories import MockRosterRepository, MockPlayerRepository
from services.tests.mocks.mock_use_case_helpers import MockRosterHelper, MockPlayerHelper
from dtos.player_dtos import PlayerSearchResult


# Helper function to create mock data for our testing of recommendation use case
def create_season(year: int, **stats) -> Dict:
    """Create a season dict with default stats if not provided"""
    defaults = {"strikeout_rate": 0.20,"walk_rate": 0.08,"isolated_power": 0.15,"on_base_percentage": 0.32,"base_running": 0.0,
        "plate_appearances": 500 }
    defaults.update(stats)
    return defaults


def create_player_seasons(player_id: int, *seasons) -> Dict:
    """Create a seasons dict for a player"""
    seasons_dict = {}
    for season in seasons:
        if isinstance(season, int):
            seasons_dict[str(season)] = create_season(season)
        elif isinstance(season, dict):
            year = season.pop("year", 2023)
            seasons_dict[str(year)] = create_season(year, **season)
    return seasons_dict


def create_player(mlbam_id: int, name: str, position: str = "RF", **seasons) -> Dict:
    """Create a player dict with seasons"""
    player = {"mlbam_id": mlbam_id,"name": name,"position": position,"seasons": {}}
    
    if seasons:
        for year, stats in seasons.items():
            player["seasons"][str(year)] = create_season(year, **stats)
    else:
        # dfault: 2023 sseason
        player["seasons"]["2023"] = create_season(2023)
    
    return player


def create_league_avg() -> Dict[str, float]:
    """Create default league average stats"""
    return {"strikeout_rate": 0.22,"walk_rate": 0.08,"isolated_power": 0.16,"on_base_percentage": 0.32,"base_running": 0.0}


def create_league_std() -> Dict[str, float]:
    """Create default league standard deviations"""
    return {"strikeout_rate": 0.03,"walk_rate": 0.02,"isolated_power": 0.04,"on_base_percentage": 0.03,"base_running": 0.}

# PYTEST FIXTURES ADDDed
@pytest.fixture
def mock_roster_repo():
    """Create a mock roster repository."""
    return MockRosterRepository()


@pytest.fixture
def mock_player_repo():
    """Create a mock player repository"""
    return MockPlayerRepository()


@pytest.fixture
def mock_roster_helper():
    """Create a mock roster use case helper"""
    return MockRosterHelper()


@pytest.fixture
def mock_player_helper():
    """Create a mock player use case helper"""
    return MockPlayerHelper()


@pytest.fixture
def service(mock_roster_repo, mock_roster_helper, mock_player_repo, mock_player_helper):
    """Returns a RecommendationService instance with mocked dependencies"""
    return RecommendationService(
        mock_roster_repo,
        mock_roster_helper,
        mock_player_repo,
        mock_player_helper
    )


# Input validation of the list of mlb ids
class TestRosterPlayerCountValidation:
    """Tests that saved teams must have at least 9 players to use the recommendation"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_roster_with_less_than_9_players_raises_error(self, service):
        """Passing less than 9 players for recommendations should raise input validation error"""
        
        player_ids = [1, 2, 3, 4, 5, 6, 7, 8]  

        with pytest.raises(InputValidationError) as exc_info:
            await service.recommend_players(player_ids)

        assert "A valid roster must contain at least 9 players" in str(exc_info.value)
        # cant check full string cause of the full error string is included iwth the input validation erro
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_roster_with_9_players_passes_validation(self, service, mock_roster_repo, mock_roster_helper, mock_player_repo, mock_player_helper):
        """Passing exactly 9 players should not raise error and correctly return the top 5 recommended players"""
        
        player_ids = list(range(1, 10)) 
        
        # add players to repostiory
        for pid in player_ids:
            mock_roster_repo.set_players_seasons_data(pid, create_player_seasons(pid, 2023))
        
        # create leageu averages
        mock_roster_repo.set_league_avg(create_league_avg())
        mock_roster_repo.set_league_std(create_league_std())
        
        # force a player to have lowest adjustment as he will be replaced with players at his posiiton
        mock_roster_helper.set_adjustment_sum(0.000000001)  
        
        # Set up roster player data where player 1 is RF will be replaced
        for pid in player_ids:
            mock_player_repo.set_player(pid, create_player(pid, f"Player {pid}", "SS" if pid != 1 else "RF"))
        
        # the RF position will be weakest player replaced
        mock_player_helper.set_primary_position("RF")
        
        # Add 5 candidates with matching RF position
        candidate_ids = [100, 101, 102, 103, 104]
        for cid in candidate_ids:
            candidate = create_player(cid, f"Candidate {cid}", "RF")
            mock_player_repo.add_player(candidate)
            mock_roster_repo.set_players_seasons_data(cid, create_player_seasons(cid, 2023))
        
        # Add a left field player testing to see if we are returing it or not
        lf_player_id = 200
        lf_candidate = create_player(lf_player_id, "LF Candidate", "LF")
        mock_player_repo.add_player(lf_candidate)
        mock_roster_repo.set_players_seasons_data(lf_player_id, create_player_seasons(lf_player_id, 2023))
        
       # resutls from actual recommendation service
        result = await service.recommend_players(player_ids)
        
        # Check if 5 players are returned
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 5, f"Expected exactly 5 recommendations, got {len(result)}"
        
        # Check if players returned are PlayerSearchResult objects
        for player in result:
            assert isinstance(player, PlayerSearchResult), f"Expected PlayerSearchResult, got {type(player)}"
            assert hasattr(player, 'id'), "Player should have id"
            assert hasattr(player, 'name'), "Player should have name"
            assert hasattr(player, 'score'), "Player should have score"
        
        # check if all players returned are RF since that is the position played by the weakest player and from our mock test
        # then correctly returns the top 5 recommendations 
        returned_ids = [player.id for player in result]
        assert set(returned_ids) == set(candidate_ids), f"Expected RF candidates {candidate_ids}, got {returned_ids}"
        

