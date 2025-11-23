"""
Unit tests for LeagueStatsDomain helper class.
"""
import pytest
from useCaseHelpers.league_stats_helper import LeagueStatsDomain
from entities.league_stats import TeamAggregate, LeagueAggregate


class TestLeagueStatsDomainComputeLeagueAggregate:
    """Tests for compute_league_aggregate method."""
    
    @pytest.fixture
    def domain(self):
        """Create a LeagueStatsDomain instance for testing."""
        return LeagueStatsDomain()
    
    @pytest.mark.unit
    def test_compute_league_aggregate_empty_teams(self, domain):
        """Test that empty teams list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            domain.compute_league_aggregate([])
        
        assert "No teams provided" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_compute_league_aggregate_no_averages(self, domain):
        """Test that teams with no averages raises ValueError."""
        teams = [
            TeamAggregate(team_id="team1", avg={}, player_count=0)
        ]
        
        with pytest.raises(ValueError) as exc_info:
            domain.compute_league_aggregate(teams)
        
        assert "No team averages available" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_compute_league_aggregate_single_team(self, domain):
        """Test league aggregate with single team."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.250, "ops": 0.750},
                player_count=25
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        assert isinstance(result, LeagueAggregate)
        assert result.teams_counted == 1
        assert result.players_counted == 25
        assert result.unweighted["batting_avg"] == 0.250
        assert result.weighted_by_player_count["batting_avg"] == 0.250
    
    @pytest.mark.unit
    def test_compute_league_aggregate_multiple_teams(self, domain):
        """Test league aggregate with multiple teams."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.250, "ops": 0.750},
                player_count=25
            ),
            TeamAggregate(
                team_id="team2",
                avg={"batting_avg": 0.260, "ops": 0.800},
                player_count=30
            ),
            TeamAggregate(
                team_id="team3",
                avg={"batting_avg": 0.240, "ops": 0.700},
                player_count=20
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        assert result.teams_counted == 3
        assert result.players_counted == 75
        # Unweighted average: (0.250 + 0.260 + 0.240) / 3 = 0.25
        assert result.unweighted["batting_avg"] == 0.25
        # Weighted average: (0.250*25 + 0.260*30 + 0.240*20) / 75
        assert result.weighted_by_player_count["batting_avg"] > 0
    
    @pytest.mark.unit
    def test_compute_league_aggregate_zero_players(self, domain):
        """Test league aggregate when total players is zero."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.250},
                player_count=0
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        assert result.players_counted == 0
        # When no players, weighted should equal unweighted
        assert result.weighted_by_player_count["batting_avg"] == result.unweighted["batting_avg"]
    
    @pytest.mark.unit
    def test_compute_league_aggregate_calculates_std(self, domain):
        """Test that standard deviations are calculated."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.250},
                player_count=25
            ),
            TeamAggregate(
                team_id="team2",
                avg={"batting_avg": 0.260},
                player_count=30
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        assert "batting_avg" in result.unweighted_std
        assert "batting_avg" in result.weighted_by_player_count_std
        assert result.unweighted_std["batting_avg"] > 0
    
    @pytest.mark.unit
    def test_compute_league_aggregate_has_timestamp(self, domain):
        """Test that result includes timestamp."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.250},
                player_count=25
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        assert result.updated_at is not None
        # Timezone-aware datetime includes +00:00 instead of Z
        assert ("Z" in result.updated_at or "+00:00" in result.updated_at)
    
    @pytest.mark.unit
    def test_compute_league_aggregate_rounds_values(self, domain):
        """Test that values are rounded to 4 decimal places."""
        teams = [
            TeamAggregate(
                team_id="team1",
                avg={"batting_avg": 0.2501234567},
                player_count=25
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        # Should be rounded to 4 decimals
        assert len(str(result.unweighted["batting_avg"]).split('.')[-1]) <= 4
    
    @pytest.mark.unit
    def test_compute_league_aggregate_filters_empty_avg(self, domain):
        """Test that teams with empty avg dict are filtered out."""
        teams = [
            TeamAggregate(team_id="team1", avg={}, player_count=0),
            TeamAggregate(
                team_id="team2",
                avg={"batting_avg": 0.250},
                player_count=25
            )
        ]
        
        result = domain.compute_league_aggregate(teams)
        
        # Should only count team2
        assert result.teams_counted == 1
        assert result.players_counted == 25
