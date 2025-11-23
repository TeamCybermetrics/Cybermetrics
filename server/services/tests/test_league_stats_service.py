"""
Unit tests for LeagueStatsService.
"""
import pytest
from unittest.mock import Mock
from services.league_stats_service import LeagueStatsService
from entities.league_stats import TeamAggregate, LeagueAggregate


class TestLeagueStatsServiceInitialization:
    """Tests for LeagueStatsService initialization."""
    
    @pytest.mark.unit
    def test_initialization(self):
        """Test service initializes with dependencies."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        service = LeagueStatsService(mock_repo, mock_domain)
        
        assert service.player_repository is mock_repo
        assert service.domain is mock_domain


class TestLeagueStatsServicePersistLeagueAggregate:
    """Tests for persist_league_aggregate method."""
    
    @pytest.mark.unit
    def test_persist_league_aggregate(self):
        """Test persisting league aggregate."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        service = LeagueStatsService(mock_repo, mock_domain)
        
        aggregate = LeagueAggregate(
            unweighted={"batting_avg": 0.250},
            weighted_by_player_count={"batting_avg": 0.250},
            unweighted_std={"batting_avg": 0.05},
            weighted_by_player_count_std={"batting_avg": 0.05},
            teams_counted=30,
            players_counted=750,
            updated_at="2023-01-01T00:00:00Z"
        )
        
        service.persist_league_aggregate(aggregate)
        
        mock_repo.set_league_averages.assert_called_once()


class TestLeagueStatsServiceBuildTeamAggregate:
    """Tests for build_team_aggregate method."""
    
    @pytest.mark.unit
    def test_build_team_aggregate(self):
        """Test building team aggregate."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        service = LeagueStatsService(mock_repo, mock_domain)
        
        result = service.build_team_aggregate("NYY", {"avg": 0.250}, 25)
        
        assert result.team_id == "NYY"
        assert result.avg == {"avg": 0.250}
        assert result.player_count == 25


class TestLeagueStatsServiceComputeAndPersist:
    """Tests for compute_and_persist method."""
    
    @pytest.mark.unit
    def test_compute_and_persist_success(self):
        """Test successful compute and persist."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        aggregate = LeagueAggregate(
            unweighted={"batting_avg": 0.250},
            weighted_by_player_count={"batting_avg": 0.250},
            unweighted_std={"batting_avg": 0.05},
            weighted_by_player_count_std={"batting_avg": 0.05},
            teams_counted=30,
            players_counted=750,
            updated_at="2023-01-01T00:00:00Z"
        )
        mock_domain.compute_league_aggregate.return_value = aggregate
        
        service = LeagueStatsService(mock_repo, mock_domain)
        
        teams = [
            TeamAggregate(team_id="NYY", avg={"avg": 0.250}, player_count=25)
        ]
        
        result = service.compute_and_persist(teams)
        
        assert result == aggregate
        mock_domain.compute_league_aggregate.assert_called_once_with(teams)
        mock_repo.set_league_averages.assert_called_once()
    
    @pytest.mark.unit
    def test_compute_and_persist_exception(self):
        """Test compute and persist handles exceptions."""
        mock_repo = Mock()
        mock_repo.set_league_averages.side_effect = Exception("DB error")
        mock_domain = Mock()
        
        aggregate = LeagueAggregate(
            unweighted={"batting_avg": 0.250},
            weighted_by_player_count={"batting_avg": 0.250},
            unweighted_std={"batting_avg": 0.05},
            weighted_by_player_count_std={"batting_avg": 0.05},
            teams_counted=30,
            players_counted=750,
            updated_at="2023-01-01T00:00:00Z"
        )
        mock_domain.compute_league_aggregate.return_value = aggregate
        
        service = LeagueStatsService(mock_repo, mock_domain)
        
        teams = [
            TeamAggregate(team_id="NYY", avg={"avg": 0.250}, player_count=25)
        ]
        
        with pytest.raises(Exception):
            service.compute_and_persist(teams)
