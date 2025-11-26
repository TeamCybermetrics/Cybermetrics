import pytest
from unittest.mock import patch
from typing import Dict
from services.recommendation_service import RecommendationService
from useCaseHelpers.errors import InputValidationError
from services.tests.mocks.mock_repositories import MockRosterRepository, MockPlayerRepository
from services.tests.mocks.mock_use_case_helpers import MockRosterHelper, MockPlayerHelper
from dtos.player_dtos import PlayerSearchResult
from useCaseHelpers.errors import QueryError


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
    async def test_roster_with_9_players_passes_validation(
        self, service, mock_roster_repo, mock_roster_helper, mock_player_repo, mock_player_helper
    ):
        """Passing exactly 9 players should not raise error and should return the top 5 recommended players."""
        # 9 players here
        player_ids = list(range(1, 10))  

        # Add season data
        for pid in player_ids:
            mock_roster_repo.set_players_seasons_data(pid, create_player_seasons(pid, 2023))

        # add league averages
        mock_roster_repo.set_league_avg(create_league_avg())
        mock_roster_repo.set_league_std(create_league_std())

        # force a player to be very week
        mock_roster_helper.set_adjustment_sum(0.000000001)

        # first player in RF will be replaced
        for pid in player_ids:
            position = "RF" if pid == 1 else "SS"
            mock_player_repo.set_player(pid, create_player(pid, f"Player {pid}", position))

        # search players with the RF position
        mock_player_helper.set_primary_position("RF")

        # Add exactly 5 RF candidates
        candidate_ids = [100, 101, 102, 103, 104]
        for cid in candidate_ids:
            mock_player_repo.add_player(create_player(cid, f"Candidate {cid}", "RF"))
            mock_roster_repo.set_players_seasons_data(cid, create_player_seasons(cid, 2023))

        # Add a non-RF candidate that we will not recommend that player
        lf_candidate = create_player(200, "LF Candidate", "LF")
        mock_player_repo.add_player(lf_candidate)
        mock_roster_repo.set_players_seasons_data(200, create_player_seasons(200, 2023))

        # what our interactor does
        result = await service.recommend_players(player_ids)

        # should return exactly 5 players
        assert isinstance(result, list)
        assert len(result) == 5, f"Expected 5 recommendations, got {len(result)}"

        # all results must be PlayerSearchResult and match the RF candidate IDs
        returned_ids = [player.id for player in result]
        assert set(returned_ids) == set(candidate_ids), (
            f"Expected RF candidates {candidate_ids}, got {returned_ids}"
        )

class TestValidatePlayerIdsCalled:
    """Tests that validate_player_ids is always called by the interactor to prevent future editing and deletion of it
    when saved players are being processed without an id"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_calls_validate_player_ids(self, service, mock_roster_repo, mock_roster_helper, mock_player_repo, mock_player_helper):
        """RecommendationService should call roster_domain.validate_player_ids to safeguard and check before further processing"""
        
        player_ids = list(range(1, 10))

        # mock up data
        for pid in player_ids:
            mock_roster_repo.set_players_seasons_data(pid, create_player_seasons(pid, 2023))
        mock_roster_repo.set_league_avg(create_league_avg())
        mock_roster_repo.set_league_std(create_league_std())
        mock_roster_helper.set_adjustment_sum(0.0001)
        mock_player_helper.set_primary_position("RF")

        # add 5 RF candidates
        for cid in [100, 101, 102, 103, 104]:
            mock_player_repo.add_player(create_player(cid, f"C{cid}", "RF"))
            mock_roster_repo.set_players_seasons_data(cid, create_player_seasons(cid, 2023))

        # Patch validate_player_ids to make it a mock so we can assert on it
        with patch.object(mock_roster_helper, 'validate_player_ids') as mock_validate:
            await service.recommend_players(player_ids)
            
            # assertion check here
            mock_validate.assert_called_once_with(player_ids)



class TestMissingSeasonData:
    """Tests that missing season data triggers QueryError."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_player_season_data_raises_query_error(self, service, mock_roster_repo, mock_roster_helper, mock_player_repo):
        """Chceks if QueryError is raised when a player dosent have any data from any seasons"""

        player_ids = list(range(1, 10))

        # populate season data for only 8 players leaving the last with no data
        for pid in player_ids[:-1]:  
            mock_roster_repo.set_players_seasons_data(pid, create_player_seasons(pid, 2023))

        # Create the data for this mock league
        mock_roster_repo.set_league_avg(create_league_avg())
        mock_roster_repo.set_league_std(create_league_std())

        # QueryError should be raised from to missing season data 
        with pytest.raises(QueryError):
            await service.recommend_players(player_ids)
