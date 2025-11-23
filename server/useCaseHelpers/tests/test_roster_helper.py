"""
Unit tests for RosterDomain helper class.
"""
import pytest
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.errors import InputValidationError
from dtos.roster_dtos import PlayerAvgStats, RosterAvgResponse


class TestRosterDomainValidatePlayerIds:
    """Tests for validate_player_ids method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_validate_player_ids_valid(self, domain):
        """Test that valid player IDs pass validation."""
        domain.validate_player_ids([1, 2, 3])
        domain.validate_player_ids([12345])
    
    @pytest.mark.unit
    def test_validate_player_ids_empty_list(self, domain):
        """Test that empty list raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.validate_player_ids([])
        
        assert "cannot be empty" in str(exc_info.value)


class TestRosterDomainCalculatePlayerAverages:
    """Tests for calculate_player_averages method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_calculate_player_averages_empty_seasons(self, domain):
        """Test that empty seasons returns None."""
        result = domain.calculate_player_averages({})
        assert result is None
    
    @pytest.mark.unit
    def test_calculate_player_averages_no_plate_appearances(self, domain):
        """Test seasons with no plate appearances returns None."""
        seasons = {
            "2023": {"plate_appearances": 0, "strikeout_rate": 0.25}
        }
        
        result = domain.calculate_player_averages(seasons)
        assert result is None
    
    @pytest.mark.unit
    def test_calculate_player_averages_single_season(self, domain):
        """Test calculating averages for single season."""
        seasons = {
            "2023": {
                "plate_appearances": 500,
                "strikeout_rate": 0.20,
                "walk_rate": 0.10,
                "isolated_power": 0.180,
                "on_base_percentage": 0.350,
                "base_running": 2.5
            }
        }
        
        result = domain.calculate_player_averages(seasons)
        
        assert isinstance(result, PlayerAvgStats)
        assert result.strikeout_rate == 0.20
        assert result.walk_rate == 0.10
    
    @pytest.mark.unit
    def test_calculate_player_averages_multiple_seasons(self, domain):
        """Test averaging across multiple seasons."""
        seasons = {
            "2022": {
                "plate_appearances": 400,
                "strikeout_rate": 0.20,
                "walk_rate": 0.10,
                "isolated_power": 0.150,
                "on_base_percentage": 0.330,
                "base_running": 2.0
            },
            "2023": {
                "plate_appearances": 500,
                "strikeout_rate": 0.24,
                "walk_rate": 0.12,
                "isolated_power": 0.170,
                "on_base_percentage": 0.350,
                "base_running": 3.0
            }
        }
        
        result = domain.calculate_player_averages(seasons)
        
        # Average of 0.20 and 0.24 = 0.22
        assert result.strikeout_rate == pytest.approx(0.22)
        # Average of 0.10 and 0.12 = 0.11
        assert result.walk_rate == pytest.approx(0.11)


class TestRosterDomainCalculateRosterAverages:
    """Tests for calculate_roster_averages method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_calculate_roster_averages_empty_dict(self, domain):
        """Test with empty players data."""
        result = domain.calculate_roster_averages({})
        
        assert isinstance(result, RosterAvgResponse)
        assert result.total_players == 0
        assert len(result.stats) == 0
    
    @pytest.mark.unit
    def test_calculate_roster_averages_single_player(self, domain):
        """Test with single player."""
        players_data = {
            12345: {
                "2023": {
                    "plate_appearances": 500,
                    "strikeout_rate": 0.20,
                    "walk_rate": 0.10,
                    "isolated_power": 0.180,
                    "on_base_percentage": 0.350,
                    "base_running": 2.5
                }
            }
        }
        
        result = domain.calculate_roster_averages(players_data)
        
        assert result.total_players == 1
        assert 12345 in result.stats


class TestRosterDomainComputeUnweightedRosterAverage:
    """Tests for compute_unweighted_roster_average_dict method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_compute_unweighted_roster_average_empty_list(self, domain):
        """Test that empty list raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.compute_unweighted_roster_average_dict([])
        
        assert "No player statistics provided" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_compute_unweighted_roster_average_all_none(self, domain):
        """Test that all None values raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.compute_unweighted_roster_average_dict([None, None])
        
        assert "No valid player statistics" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_compute_unweighted_roster_average_single_player(self, domain):
        """Test averaging with single player."""
        stats = [
            PlayerAvgStats(
                strikeout_rate=0.20,
                walk_rate=0.10,
                isolated_power=0.180,
                on_base_percentage=0.350,
                base_running=2.5
            )
        ]
        
        result = domain.compute_unweighted_roster_average_dict(stats)
        
        assert result["strikeout_rate"] == 0.20
        assert result["walk_rate"] == 0.10
    
    @pytest.mark.unit
    def test_compute_unweighted_roster_average_multiple_players(self, domain):
        """Test averaging with multiple players."""
        stats = [
            PlayerAvgStats(
                strikeout_rate=0.20,
                walk_rate=0.10,
                isolated_power=0.150,
                on_base_percentage=0.330,
                base_running=2.0
            ),
            PlayerAvgStats(
                strikeout_rate=0.24,
                walk_rate=0.12,
                isolated_power=0.170,
                on_base_percentage=0.350,
                base_running=3.0
            )
        ]
        
        result = domain.compute_unweighted_roster_average_dict(stats)
        
        assert result["strikeout_rate"] == pytest.approx(0.22)
        assert result["walk_rate"] == pytest.approx(0.11)


class TestRosterDomainComputeTeamWeaknessScores:
    """Tests for compute_team_weakness_scores method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_compute_team_weakness_scores_basic(self, domain):
        """Test basic weakness score calculation."""
        team_avg = {
            "strikeout_rate": 0.22,
            "walk_rate": 0.09,
            "isolated_power": 0.150,
            "on_base_percentage": 0.320,
            "base_running": 1.5
        }
        league_avg = {
            "strikeout_rate": 0.23,
            "walk_rate": 0.08,
            "isolated_power": 0.160,
            "on_base_percentage": 0.315,
            "base_running": 2.0
        }
        league_std = {
            "strikeout_rate": 0.02,
            "walk_rate": 0.01,
            "isolated_power": 0.02,
            "on_base_percentage": 0.015,
            "base_running": 0.5
        }
        
        result = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        
        assert "strikeout_rate" in result
        assert "walk_rate" in result
        assert isinstance(result["strikeout_rate"], float)
    
    @pytest.mark.unit
    def test_compute_team_weakness_scores_zero_std(self, domain):
        """Test that zero std is handled (uses 10^5 as denominator)."""
        team_avg = {"strikeout_rate": 0.22}
        league_avg = {"strikeout_rate": 0.23}
        league_std = {"strikeout_rate": 0.0}
        
        result = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        
        # Should not raise division by zero
        assert "strikeout_rate" in result


class TestRosterDomainCalculatePlayerLatestWar:
    """Tests for calculate_player_latest_war method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_calculate_player_latest_war_empty_seasons(self, domain):
        """Test with empty seasons."""
        result = domain.calculate_player_latest_war({})
        assert result is None
    
    @pytest.mark.unit
    def test_calculate_player_latest_war_single_season(self, domain):
        """Test with single season."""
        seasons = {
            "2023": {
                "plate_appearances": 500,
                "war": 5.5
            }
        }
        
        result = domain.calculate_player_latest_war(seasons)
        assert result == 5.5
    
    @pytest.mark.unit
    def test_calculate_player_latest_war_multiple_seasons(self, domain):
        """Test that most recent season is used."""
        seasons = {
            "2021": {"plate_appearances": 400, "war": 3.0},
            "2022": {"plate_appearances": 450, "war": 4.0},
            "2023": {"plate_appearances": 500, "war": 5.5}
        }
        
        result = domain.calculate_player_latest_war(seasons)
        assert result == 5.5
    
    @pytest.mark.unit
    def test_calculate_player_latest_war_no_plate_appearances(self, domain):
        """Test seasons with no plate appearances."""
        seasons = {
            "2023": {"plate_appearances": 0, "war": 0.0}
        }
        
        result = domain.calculate_player_latest_war(seasons)
        assert result is None


class TestRosterDomainGetPlayerLatestStats:
    """Tests for get_player_latest_stats method."""
    
    @pytest.fixture
    def domain(self):
        """Create a RosterDomain instance for testing."""
        return RosterDomain()
    
    @pytest.mark.unit
    def test_get_player_latest_stats_empty_seasons(self, domain):
        """Test with empty seasons."""
        result = domain.get_player_latest_stats({})
        assert result is None
    
    @pytest.mark.unit
    def test_get_player_latest_stats_single_season(self, domain):
        """Test with single season."""
        seasons = {
            "2023": {
                "plate_appearances": 500,
                "strikeout_rate": 0.20,
                "walk_rate": 0.10,
                "isolated_power": 0.180,
                "on_base_percentage": 0.350,
                "base_running": 2.5
            }
        }
        
        result = domain.get_player_latest_stats(seasons)
        
        assert result is not None
        assert result["strikeout_rate"] == 0.20
        assert result["walk_rate"] == 0.10
    
    @pytest.mark.unit
    def test_get_player_latest_stats_fallback_to_recent(self, domain):
        """Test fallback to most recent season even if PA == 0."""
        seasons = {
            "2023": {
                "plate_appearances": 0,
                "strikeout_rate": 0.20
            }
        }
        
        result = domain.get_player_latest_stats(seasons)
        
        # Should still return stats even with 0 PA
        assert result is not None
        assert "strikeout_rate" in result
