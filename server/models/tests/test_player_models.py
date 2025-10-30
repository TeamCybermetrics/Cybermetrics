import pytest
from pydantic import ValidationError
from models.players import (
    PlayerSearchResult, AddPlayerResponse, DeletePlayerResponse,
    SavedPlayer, SeasonStats, PlayerDetail, RosterAvgRequest,
    PlayerAvgStats, RosterAvgResponse
)


class TestPlayerModels:
    """Unit tests for player models"""
    
    # Test PlayerSearchResult
    def test_player_search_result_valid(self):
        """Test creating valid PlayerSearchResult"""
        result = PlayerSearchResult(
            id=545361,
            name="Mike Trout",
            score=95.5,
            image_url="https://example.com/image.jpg",
            years_active="2011-2023"
        )
        assert result.id == 545361
        assert result.name == "Mike Trout"
        assert result.score == 95.5
        assert result.image_url == "https://example.com/image.jpg"
        assert result.years_active == "2011-2023"
    
    def test_player_search_result_missing_fields(self):
        """Test PlayerSearchResult with missing required fields"""
        with pytest.raises(ValidationError):
            PlayerSearchResult(
                id=545361,
                name="Mike Trout",
                score=95.5
            )
    
    # Test AddPlayerResponse
    def test_add_player_response_valid(self):
        """Test creating valid AddPlayerResponse"""
        response = AddPlayerResponse(
            message="Player added successfully",
            player_id="545361"
        )
        assert response.message == "Player added successfully"
        assert response.player_id == "545361"
    
    # Test DeletePlayerResponse
    def test_delete_player_response_valid(self):
        """Test creating valid DeletePlayerResponse"""
        response = DeletePlayerResponse(
            message="Player deleted successfully"
        )
        assert response.message == "Player deleted successfully"
    
    # Test SavedPlayer
    def test_saved_player_valid(self):
        """Test creating valid SavedPlayer"""
        player = SavedPlayer(
            id=545361,
            name="Mike Trout",
            image_url="https://example.com/image.jpg",
            years_active="2011-2023"
        )
        assert player.id == 545361
        assert player.name == "Mike Trout"
        assert player.image_url == "https://example.com/image.jpg"
        assert player.years_active == "2011-2023"
    
    def test_saved_player_optional_fields(self):
        """Test SavedPlayer with optional fields"""
        player = SavedPlayer(
            id=545361,
            name="Mike Trout"
        )
        assert player.image_url is None
        assert player.years_active is None
    
    def test_saved_player_extra_fields(self):
        """Test SavedPlayer allows extra fields"""
        player = SavedPlayer(
            id=545361,
            name="Mike Trout",
            team="LAA",
            position="OF"
        )
        assert player.id == 545361
        assert player.name == "Mike Trout"
    
    # Test SeasonStats
    def test_season_stats_valid(self):
        """Test creating valid SeasonStats"""
        stats = SeasonStats(
            games=150,
            plate_appearances=600,
            at_bats=550,
            hits=180,
            home_runs=40,
            batting_average=0.327,
            on_base_percentage=0.410,
            slugging_percentage=0.645
        )
        assert stats.games == 150
        assert stats.plate_appearances == 600
        assert stats.batting_average == 0.327
    
    def test_season_stats_defaults(self):
        """Test SeasonStats with default values"""
        stats = SeasonStats()
        assert stats.games == 0
        assert stats.plate_appearances == 0
        assert stats.batting_average == 0.0
        assert stats.war == 0.0
    
    def test_season_stats_def_field(self):
        """Test SeasonStats with def_ field (Python keyword)"""
        stats = SeasonStats(def_=10.5)
        assert stats.def_ == 10.5
    
    def test_season_stats_optional_fields(self):
        """Test SeasonStats with optional contact quality fields"""
        stats = SeasonStats(
            hard_hit_rate=45.5,
            barrel_rate=12.3,
            avg_exit_velocity=92.5,
            avg_launch_angle=15.2
        )
        assert stats.hard_hit_rate == 45.5
        assert stats.barrel_rate == 12.3
        assert stats.avg_exit_velocity == 92.5
        assert stats.avg_launch_angle == 15.2
    
    # Test PlayerDetail
    def test_player_detail_valid(self):
        """Test creating valid PlayerDetail"""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/image.jpg",
            years_active="2011-2023",
            team_abbrev="LAA",
            overall_score=95.5,
            seasons={
                "2023": SeasonStats(games=150, plate_appearances=600)
            }
        )
        assert detail.mlbam_id == 545361
        assert detail.fangraphs_id == 10155
        assert detail.name == "Mike Trout"
        assert "2023" in detail.seasons
        assert isinstance(detail.seasons["2023"], SeasonStats)
    
    def test_player_detail_optional_fields(self):
        """Test PlayerDetail with optional fields"""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/image.jpg",
            years_active="2011-2023",
            seasons={}
        )
        assert detail.team_abbrev is None
        assert detail.overall_score == 0.0
    
    def test_player_detail_missing_required_fields(self):
        """Test PlayerDetail with missing required fields"""
        with pytest.raises(ValidationError):
            PlayerDetail(
                mlbam_id=545361,
                name="Mike Trout",
                image_url="https://example.com/image.jpg"
            )
    
    # Test RosterAvgRequest
    def test_roster_avg_request_valid(self):
        """Test creating valid RosterAvgRequest"""
        request = RosterAvgRequest(
            player_ids=[545361, 660271, 592450]
        )
        assert len(request.player_ids) == 3
        assert 545361 in request.player_ids
    
    def test_roster_avg_request_single_player(self):
        """Test RosterAvgRequest with single player"""
        request = RosterAvgRequest(player_ids=[545361])
        assert len(request.player_ids) == 1
    
    def test_roster_avg_request_empty_list(self):
        """Test RosterAvgRequest with empty list fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            RosterAvgRequest(player_ids=[])
        assert "min_items" in str(exc_info.value).lower() or "at least" in str(exc_info.value).lower()
    
    def test_roster_avg_request_missing_field(self):
        """Test RosterAvgRequest with missing required field"""
        with pytest.raises(ValidationError):
            RosterAvgRequest()
    
    # Test PlayerAvgStats
    def test_player_avg_stats_valid(self):
        """Test creating valid PlayerAvgStats"""
        stats = PlayerAvgStats(
            strikeout_rate=0.200,
            walk_rate=0.150,
            isolated_power=0.250,
            on_base_percentage=0.380,
            base_running=2.5
        )
        assert stats.strikeout_rate == 0.200
        assert stats.walk_rate == 0.150
        assert stats.isolated_power == 0.250
        assert stats.on_base_percentage == 0.380
        assert stats.base_running == 2.5
    
    def test_player_avg_stats_missing_fields(self):
        """Test PlayerAvgStats with missing required fields"""
        with pytest.raises(ValidationError):
            PlayerAvgStats(
                strikeout_rate=0.200,
                walk_rate=0.150
            )
    
    # Test RosterAvgResponse
    def test_roster_avg_response_valid(self):
        """Test creating valid RosterAvgResponse"""
        response = RosterAvgResponse(
            stats={
                545361: PlayerAvgStats(
                    strikeout_rate=0.200,
                    walk_rate=0.150,
                    isolated_power=0.250,
                    on_base_percentage=0.380,
                    base_running=2.5
                ),
                660271: PlayerAvgStats(
                    strikeout_rate=0.180,
                    walk_rate=0.120,
                    isolated_power=0.220,
                    on_base_percentage=0.350,
                    base_running=1.5
                )
            },
            total_players=2
        )
        assert response.total_players == 2
        assert 545361 in response.stats
        assert 660271 in response.stats
        assert isinstance(response.stats[545361], PlayerAvgStats)
    
    def test_roster_avg_response_empty(self):
        """Test RosterAvgResponse with no players"""
        response = RosterAvgResponse(
            stats={},
            total_players=0
        )
        assert response.total_players == 0
        assert len(response.stats) == 0
    
    def test_roster_avg_response_missing_fields(self):
        """Test RosterAvgResponse with missing required fields"""
        with pytest.raises(ValidationError):
            RosterAvgResponse(stats={})
        
        with pytest.raises(ValidationError):
            RosterAvgResponse(total_players=0)
