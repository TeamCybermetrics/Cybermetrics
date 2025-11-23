"""
Unit tests for RosterRepositoryFirebase with mocked Firebase.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from infrastructure.roster_repository import RosterRepositoryFirebase


class TestRosterRepositoryInitialization:
    """Tests for RosterRepositoryFirebase initialization."""
    
    @pytest.mark.unit
    def test_repository_initialization(self):
        """Test that repository initializes with dependencies."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        assert repo.db is mock_db
        assert repo.player_repository is mock_player_repo


class TestRosterRepositoryGetPlayersData:
    """Tests for get_players_seasons_data method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_players_seasons_data_no_db(self):
        """Test get_players_seasons_data raises error when database is None."""
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(None, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_players_seasons_data([12345])
        
        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail.lower()


class TestRosterRepositoryGetLeagueUnweightedAverage:
    """Tests for get_league_unweighted_average method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_average_no_db(self):
        """Test get_league_unweighted_average raises error when database is None."""
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(None, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_average()
        
        assert exc_info.value.status_code == 503


class TestRosterRepositoryGetLeagueUnweightedStd:
    """Tests for get_league_unweighted_std method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_std_no_db(self):
        """Test get_league_unweighted_std raises error when database is None."""
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(None, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_std()
        
        assert exc_info.value.status_code == 503


class TestRosterRepositoryGetPlayersDataSuccess:
    """Tests for successful get_players_seasons_data."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_players_seasons_data_from_cache(self):
        """Test getting players data from cache."""
        mock_db = Mock()
        mock_player_repo = Mock()
        mock_player_repo._ensure_cache_loaded = AsyncMock()
        mock_player_repo._players_cache_by_id = {
            12345: {"mlbam_id": 12345, "seasons": {"2023": {}}},
            67890: {"mlbam_id": 67890, "seasons": {"2023": {}}}
        }
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_players_seasons_data([12345, 67890])
        
        assert len(result) == 2
        assert 12345 in result
        assert 67890 in result


class TestRosterRepositoryGetLeagueWeightedStd:
    """Tests for get_league_weighted_std method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_weighted_std_no_db(self):
        """Test get_league_weighted_std raises error when database is None."""
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(None, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_weighted_std()
        
        assert exc_info.value.status_code == 503
