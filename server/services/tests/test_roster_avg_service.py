import pytest
from unittest.mock import AsyncMock, Mock
from services.roster_avg_service import RosterAvgService
from models.players import RosterAvgResponse, PlayerAvgStats


class TestRosterAvgService:
    """Unit tests for RosterAvgService"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_roster_repository = Mock()
        self.mock_roster_domain = Mock()
        self.mock_player_repository = Mock()
        self.roster_avg_service = RosterAvgService(
            roster_repository=self.mock_roster_repository,
            roster_domain=self.mock_roster_domain,
            player_repository=self.mock_player_repository
        )
    
    # Test get_roster_averages
    @pytest.mark.asyncio
    async def test_get_roster_averages_success(self):
        """Test successfully calculating roster averages"""
        player_ids = [545361, 660271, 592450]
        
        # Mock domain validation
        self.mock_roster_domain.validate_player_ids.return_value = None
        
        # Mock repository response
        mock_players_data = {
            545361: {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.200,
                    "walk_rate": 0.150,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            },
            660271: {
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
        self.mock_roster_repository.get_players_seasons_data = AsyncMock(
            return_value=mock_players_data
        )
        
        # Mock domain calculation
        expected_response = RosterAvgResponse(
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
        self.mock_roster_domain.calculate_roster_averages.return_value = expected_response
        
        result = await self.roster_avg_service.get_roster_averages(player_ids)
        
        # Verify domain validation was called
        self.mock_roster_domain.validate_player_ids.assert_called_once_with(player_ids)
        
        # Verify repository was called
        self.mock_roster_repository.get_players_seasons_data.assert_called_once_with(player_ids)
        
        # Verify domain calculation was called
        self.mock_roster_domain.calculate_roster_averages.assert_called_once_with(mock_players_data)
        
        # Verify response
        assert result == expected_response
        assert result.total_players == 2
        assert 545361 in result.stats
        assert 660271 in result.stats
    
    @pytest.mark.asyncio
    async def test_get_roster_averages_empty_list(self):
        """Test roster averages with empty player list"""
        player_ids = []
        
        # Mock domain validation to raise exception
        from fastapi import HTTPException, status
        self.mock_roster_domain.validate_player_ids.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player IDs list cannot be empty"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.roster_avg_service.get_roster_averages(player_ids)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify repository was not called
        self.mock_roster_repository.get_players_seasons_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_roster_averages_single_player(self):
        """Test roster averages with single player"""
        player_ids = [545361]
        
        # Mock domain validation
        self.mock_roster_domain.validate_player_ids.return_value = None
        
        # Mock repository response
        mock_players_data = {
            545361: {
                "2022": {
                    "plate_appearances": 500,
                    "strikeout_rate": 0.190,
                    "walk_rate": 0.140,
                    "isolated_power": 0.240,
                    "on_base_percentage": 0.370,
                    "base_running": 2.0
                },
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.210,
                    "walk_rate": 0.160,
                    "isolated_power": 0.260,
                    "on_base_percentage": 0.390,
                    "base_running": 3.0
                }
            }
        }
        self.mock_roster_repository.get_players_seasons_data = AsyncMock(
            return_value=mock_players_data
        )
        
        # Mock domain calculation (should average across seasons)
        expected_response = RosterAvgResponse(
            stats={
                545361: PlayerAvgStats(
                    strikeout_rate=0.200,  # Average of 0.190 and 0.210
                    walk_rate=0.150,       # Average of 0.140 and 0.160
                    isolated_power=0.250,  # Average of 0.240 and 0.260
                    on_base_percentage=0.380,  # Average of 0.370 and 0.390
                    base_running=2.5       # Average of 2.0 and 3.0
                )
            },
            total_players=1
        )
        self.mock_roster_domain.calculate_roster_averages.return_value = expected_response
        
        result = await self.roster_avg_service.get_roster_averages(player_ids)
        
        # Verify response
        assert result.total_players == 1
        assert 545361 in result.stats
    
    @pytest.mark.asyncio
    async def test_get_roster_averages_player_not_found(self):
        """Test roster averages when some players don't exist"""
        player_ids = [545361, 999999]
        
        # Mock domain validation
        self.mock_roster_domain.validate_player_ids.return_value = None
        
        # Mock repository response (only returns data for existing player)
        mock_players_data = {
            545361: {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.200,
                    "walk_rate": 0.150,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            }
            # 999999 not found
        }
        self.mock_roster_repository.get_players_seasons_data = AsyncMock(
            return_value=mock_players_data
        )
        
        # Mock domain calculation
        expected_response = RosterAvgResponse(
            stats={
                545361: PlayerAvgStats(
                    strikeout_rate=0.200,
                    walk_rate=0.150,
                    isolated_power=0.250,
                    on_base_percentage=0.380,
                    base_running=2.5
                )
            },
            total_players=1
        )
        self.mock_roster_domain.calculate_roster_averages.return_value = expected_response
        
        result = await self.roster_avg_service.get_roster_averages(player_ids)
        
        # Verify response only includes found player
        assert result.total_players == 1
        assert 545361 in result.stats
        assert 999999 not in result.stats
    
    @pytest.mark.asyncio
    async def test_get_roster_averages_no_valid_stats(self):
        """Test roster averages when players have no valid stats"""
        player_ids = [545361]
        
        # Mock domain validation
        self.mock_roster_domain.validate_player_ids.return_value = None
        
        # Mock repository response (player exists but no seasons with PA)
        mock_players_data = {
            545361: {
                "2023": {
                    "plate_appearances": 0  # No plate appearances
                }
            }
        }
        self.mock_roster_repository.get_players_seasons_data = AsyncMock(
            return_value=mock_players_data
        )
        
        # Mock domain calculation (filters out players with no valid stats)
        expected_response = RosterAvgResponse(
            stats={},
            total_players=0
        )
        self.mock_roster_domain.calculate_roster_averages.return_value = expected_response
        
        result = await self.roster_avg_service.get_roster_averages(player_ids)
        
        # Verify response has no players
        assert result.total_players == 0
        assert len(result.stats) == 0
