import pytest
from fastapi import HTTPException, status
from domain.roster_domain import RosterDomain
from models.players import PlayerAvgStats, RosterAvgResponse


class TestRosterDomain:
    """Unit tests for RosterDomain business logic"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.roster_domain = RosterDomain()
    
    # Test validate_player_ids
    def test_validate_player_ids_valid(self):
        """Test validation passes with valid player IDs"""
        player_ids = [12345, 67890, 11111]
        # Should not raise any exception
        self.roster_domain.validate_player_ids(player_ids)
    
    def test_validate_player_ids_empty_list(self):
        """Test validation fails with empty list"""
        with pytest.raises(HTTPException) as exc_info:
            self.roster_domain.validate_player_ids([])
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player IDs list cannot be empty" in str(exc_info.value.detail)
    
    def test_validate_player_ids_none(self):
        """Test validation fails with None"""
        with pytest.raises(HTTPException) as exc_info:
            self.roster_domain.validate_player_ids(None)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player IDs list cannot be empty" in str(exc_info.value.detail)
    
    # Test calculate_player_averages
    def test_calculate_player_averages_single_season(self):
        """Test calculating averages for single season"""
        seasons = {
            "2023": {
                "plate_appearances": 600,
                "strikeout_rate": 0.200,
                "walk_rate": 0.150,
                "isolated_power": 0.250,
                "on_base_percentage": 0.380,
                "base_running": 2.5
            }
        }
        
        result = self.roster_domain.calculate_player_averages(seasons)
        
        assert isinstance(result, PlayerAvgStats)
        assert result.strikeout_rate == 0.200
        assert result.walk_rate == 0.150
        assert result.isolated_power == 0.250
        assert result.on_base_percentage == 0.380
        assert result.base_running == 2.5
    
    def test_calculate_player_averages_multiple_seasons(self):
        """Test calculating averages across multiple seasons"""
        seasons = {
            "2022": {
                "plate_appearances": 500,
                "strikeout_rate": 0.200,
                "walk_rate": 0.100,
                "isolated_power": 0.200,
                "on_base_percentage": 0.350,
                "base_running": 2.0
            },
            "2023": {
                "plate_appearances": 600,
                "strikeout_rate": 0.240,
                "walk_rate": 0.140,
                "isolated_power": 0.260,
                "on_base_percentage": 0.370,
                "base_running": 3.0
            }
        }
        
        result = self.roster_domain.calculate_player_averages(seasons)
        
        assert isinstance(result, PlayerAvgStats)
        # Average of 0.200 and 0.240 = 0.220
        assert result.strikeout_rate == 0.220
        # Average of 0.100 and 0.140 = 0.120
        assert result.walk_rate == 0.120
        # Average of 0.200 and 0.260 = 0.230
        assert result.isolated_power == 0.230
        # Average of 0.350 and 0.370 = 0.360
        assert result.on_base_percentage == 0.360
        # Average of 2.0 and 3.0 = 2.5
        assert result.base_running == 2.5
    
    def test_calculate_player_averages_ignores_zero_pa(self):
        """Test that seasons with zero plate appearances are ignored"""
        seasons = {
            "2021": {
                "plate_appearances": 0,
                "strikeout_rate": 0.500,  # Should be ignored
                "walk_rate": 0.500,
                "isolated_power": 0.500,
                "on_base_percentage": 0.500,
                "base_running": 10.0
            },
            "2023": {
                "plate_appearances": 600,
                "strikeout_rate": 0.200,
                "walk_rate": 0.150,
                "isolated_power": 0.250,
                "on_base_percentage": 0.380,
                "base_running": 2.5
            }
        }
        
        result = self.roster_domain.calculate_player_averages(seasons)
        
        # Should only use 2023 data
        assert result.strikeout_rate == 0.200
        assert result.walk_rate == 0.150
    
    def test_calculate_player_averages_empty_seasons(self):
        """Test calculating averages with no seasons returns None"""
        seasons = {}
        result = self.roster_domain.calculate_player_averages(seasons)
        assert result is None
    
    def test_calculate_player_averages_none(self):
        """Test calculating averages with None returns None"""
        result = self.roster_domain.calculate_player_averages(None)
        assert result is None
    
    def test_calculate_player_averages_all_zero_pa(self):
        """Test calculating averages when all seasons have zero PA returns None"""
        seasons = {
            "2022": {
                "plate_appearances": 0,
                "strikeout_rate": 0.200
            },
            "2023": {
                "plate_appearances": 0,
                "strikeout_rate": 0.250
            }
        }
        
        result = self.roster_domain.calculate_player_averages(seasons)
        assert result is None
    
    def test_calculate_player_averages_missing_stats(self):
        """Test calculating averages with missing stats uses defaults"""
        seasons = {
            "2023": {
                "plate_appearances": 600
                # Missing all stat fields
            }
        }
        
        result = self.roster_domain.calculate_player_averages(seasons)
        
        assert isinstance(result, PlayerAvgStats)
        assert result.strikeout_rate == 0.0
        assert result.walk_rate == 0.0
        assert result.isolated_power == 0.0
        assert result.on_base_percentage == 0.0
        assert result.base_running == 0.0
    
    # Test calculate_roster_averages
    def test_calculate_roster_averages_single_player(self):
        """Test calculating roster averages for single player"""
        players_data = {
            12345: {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.200,
                    "walk_rate": 0.150,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            }
        }
        
        result = self.roster_domain.calculate_roster_averages(players_data)
        
        assert isinstance(result, RosterAvgResponse)
        assert result.total_players == 1
        assert 12345 in result.stats
        assert isinstance(result.stats[12345], PlayerAvgStats)
    
    def test_calculate_roster_averages_multiple_players(self):
        """Test calculating roster averages for multiple players"""
        players_data = {
            12345: {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.200,
                    "walk_rate": 0.150,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            },
            67890: {
                "2023": {
                    "plate_appearances": 550,
                    "strikeout_rate": 0.180,
                    "walk_rate": 0.120,
                    "isolated_power": 0.220,
                    "on_base_percentage": 0.350,
                    "base_running": 1.5
                }
            }
        }
        
        result = self.roster_domain.calculate_roster_averages(players_data)
        
        assert isinstance(result, RosterAvgResponse)
        assert result.total_players == 2
        assert 12345 in result.stats
        assert 67890 in result.stats
    
    def test_calculate_roster_averages_filters_invalid_players(self):
        """Test that players with no valid stats are filtered out"""
        players_data = {
            12345: {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.200,
                    "walk_rate": 0.150,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            },
            67890: {}  # No seasons
        }
        
        result = self.roster_domain.calculate_roster_averages(players_data)
        
        assert result.total_players == 1
        assert 12345 in result.stats
        assert 67890 not in result.stats
    
    def test_calculate_roster_averages_empty_data(self):
        """Test calculating roster averages with empty data"""
        players_data = {}
        
        result = self.roster_domain.calculate_roster_averages(players_data)
        
        assert isinstance(result, RosterAvgResponse)
        assert result.total_players == 0
        assert len(result.stats) == 0
