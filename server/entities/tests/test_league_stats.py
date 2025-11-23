"""
Unit tests for league stats entities.
"""
import pytest
from pydantic import ValidationError
from entities.league_stats import TeamAggregate, LeagueAggregate


class TestTeamAggregate:
    """Tests for TeamAggregate entity."""
    
    @pytest.mark.unit
    def test_team_aggregate_valid_creation(self):
        """Test creating a valid TeamAggregate."""
        team = TeamAggregate(
            team_id="team123",
            avg={"batting_avg": 0.250, "ops": 0.750},
            player_count=25
        )
        
        assert team.team_id == "team123"
        assert team.avg["batting_avg"] == 0.250
        assert team.player_count == 25
    
    @pytest.mark.unit
    def test_team_aggregate_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            TeamAggregate(
                team_id="team123",
                avg={"batting_avg": 0.250}
                # Missing player_count
            )
    
    @pytest.mark.unit
    def test_team_aggregate_negative_player_count(self):
        """Test that negative player_count raises ValidationError."""
        with pytest.raises(ValidationError):
            TeamAggregate(
                team_id="team123",
                avg={"batting_avg": 0.250},
                player_count=-5
            )
    
    @pytest.mark.unit
    def test_team_aggregate_zero_player_count(self):
        """Test that zero player_count is allowed."""
        team = TeamAggregate(
            team_id="team123",
            avg={},
            player_count=0
        )
        
        assert team.player_count == 0
    
    @pytest.mark.unit
    def test_team_aggregate_empty_avg_dict(self):
        """Test TeamAggregate with empty avg dictionary."""
        team = TeamAggregate(
            team_id="team123",
            avg={},
            player_count=0
        )
        
        assert team.avg == {}
    
    @pytest.mark.unit
    def test_team_aggregate_to_dict(self):
        """Test converting TeamAggregate to dictionary."""
        team = TeamAggregate(
            team_id="team123",
            avg={"batting_avg": 0.250},
            player_count=25
        )
        
        team_dict = team.model_dump()
        assert isinstance(team_dict, dict)
        assert team_dict["team_id"] == "team123"
        assert team_dict["player_count"] == 25


class TestLeagueAggregate:
    """Tests for LeagueAggregate entity."""
    
    @pytest.mark.unit
    def test_league_aggregate_valid_creation(self):
        """Test creating a valid LeagueAggregate."""
        league = LeagueAggregate(
            unweighted={"batting_avg": 0.250},
            weighted_by_player_count={"batting_avg": 0.255},
            unweighted_std={"batting_avg": 0.025},
            weighted_by_player_count_std={"batting_avg": 0.020},
            teams_counted=30,
            players_counted=750,
            updated_at="2024-01-01T00:00:00Z"
        )
        
        assert league.teams_counted == 30
        assert league.players_counted == 750
        assert league.unweighted["batting_avg"] == 0.250
    
    @pytest.mark.unit
    def test_league_aggregate_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            LeagueAggregate(
                unweighted={"batting_avg": 0.250},
                weighted_by_player_count={"batting_avg": 0.255},
                unweighted_std={"batting_avg": 0.025},
                weighted_by_player_count_std={"batting_avg": 0.020},
                teams_counted=30,
                players_counted=750
                # Missing updated_at
            )
    
    @pytest.mark.unit
    def test_league_aggregate_all_fields_present(self):
        """Test that all required fields are present."""
        league = LeagueAggregate(
            unweighted={},
            weighted_by_player_count={},
            unweighted_std={},
            weighted_by_player_count_std={},
            teams_counted=0,
            players_counted=0,
            updated_at="2024-01-01"
        )
        
        assert league.teams_counted == 0
        assert league.players_counted == 0
        assert league.updated_at == "2024-01-01"
    
    @pytest.mark.unit
    def test_league_aggregate_empty_dicts(self):
        """Test LeagueAggregate with empty stat dictionaries."""
        league = LeagueAggregate(
            unweighted={},
            weighted_by_player_count={},
            unweighted_std={},
            weighted_by_player_count_std={},
            teams_counted=0,
            players_counted=0,
            updated_at="2024-01-01"
        )
        
        assert league.unweighted == {}
        assert league.weighted_by_player_count == {}
    
    @pytest.mark.unit
    def test_league_aggregate_multiple_stats(self):
        """Test LeagueAggregate with multiple statistics."""
        league = LeagueAggregate(
            unweighted={
                "batting_avg": 0.250,
                "ops": 0.750,
                "war": 2.5
            },
            weighted_by_player_count={
                "batting_avg": 0.255,
                "ops": 0.760,
                "war": 2.7
            },
            unweighted_std={
                "batting_avg": 0.025,
                "ops": 0.050,
                "war": 0.5
            },
            weighted_by_player_count_std={
                "batting_avg": 0.020,
                "ops": 0.045,
                "war": 0.4
            },
            teams_counted=30,
            players_counted=750,
            updated_at="2024-01-01"
        )
        
        assert len(league.unweighted) == 3
        assert league.unweighted["war"] == 2.5
    
    @pytest.mark.unit
    def test_league_aggregate_to_dict(self):
        """Test converting LeagueAggregate to dictionary."""
        league = LeagueAggregate(
            unweighted={"batting_avg": 0.250},
            weighted_by_player_count={"batting_avg": 0.255},
            unweighted_std={"batting_avg": 0.025},
            weighted_by_player_count_std={"batting_avg": 0.020},
            teams_counted=30,
            players_counted=750,
            updated_at="2024-01-01"
        )
        
        league_dict = league.model_dump()
        assert isinstance(league_dict, dict)
        assert league_dict["teams_counted"] == 30
        assert "unweighted" in league_dict
