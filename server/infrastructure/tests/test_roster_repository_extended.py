"""
Extended unit tests for RosterRepositoryFirebase with comprehensive coverage.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from infrastructure.roster_repository import RosterRepositoryFirebase


class TestRosterRepositoryGetPlayersDataMissingPlayers:
    """Tests for get_players_seasons_data with missing players."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_players_seasons_data_missing_players(self):
        """Test getting players data when some players are missing."""
        mock_db = Mock()
        mock_player_repo = Mock()
        mock_player_repo._ensure_cache_loaded = AsyncMock()
        mock_player_repo._players_cache_by_id = {
            12345: {"mlbam_id": 12345, "seasons": {"2023": {}}}
            # 67890 is missing
        }
        # Mock get_player_by_id to return None for missing player
        mock_player_repo.get_player_by_id = AsyncMock(return_value=None)
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_players_seasons_data([12345, 67890])
        
        # Should only return data for found player
        assert len(result) == 1
        assert 12345 in result
        assert 67890 not in result


class TestRosterRepositoryGetLeagueUnweightedAverageSuccess:
    """Tests for successful get_league_unweighted_average."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_average_from_cache(self):
        """Test getting league average from cache."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        repo._league_avg_cache = {"avg": 0.250}
        
        result = await repo.get_league_unweighted_average()
        
        assert result == {"avg": 0.250}


class TestRosterRepositoryGetLeagueUnweightedStdSuccess:
    """Tests for successful get_league_unweighted_std."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_std_from_cache(self):
        """Test getting league std from cache."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        repo._league_std_cache = {"std": 0.050}
        
        result = await repo.get_league_unweighted_std()
        
        assert result == {"std": 0.050}


class TestRosterRepositoryGetPlayersDataFallback:
    """Tests for get_players_seasons_data fallback to Firestore."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_players_seasons_data_fallback_to_firestore(self):
        """Test fallback to Firestore when player not in cache."""
        mock_db = Mock()
        mock_player_repo = Mock()
        mock_player_repo._ensure_cache_loaded = AsyncMock()
        mock_player_repo._players_cache_by_id = {}  # Empty cache
        
        # Mock get_player_by_id to return player data
        mock_player_repo.get_player_by_id = AsyncMock(return_value={
            "mlbam_id": 12345,
            "seasons": {"2023": {"games": 100}}
        })
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_players_seasons_data([12345])
        
        assert len(result) == 1
        assert 12345 in result
        assert result[12345] == {"2023": {"games": 100}}


class TestRosterRepositoryGetLeagueUnweightedBlocking:
    """Tests for _get_league_unweighted_blocking method."""
    
    @pytest.mark.unit
    def test_get_league_unweighted_blocking_not_found(self):
        """Test when league averages document not found."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_blocking()
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    def test_get_league_unweighted_blocking_malformed(self):
        """Test when unweighted data is malformed."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"unweighted": "not_a_dict"}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_blocking()
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    def test_get_league_unweighted_blocking_missing_keys(self):
        """Test when required keys are missing."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "unweighted": {
                "strikeout_rate": 0.23,
                # Missing other required keys
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_blocking()
        
        assert exc_info.value.status_code == 500
        assert "missing or non-numeric" in exc_info.value.detail
    
    @pytest.mark.unit
    def test_get_league_unweighted_blocking_success(self):
        """Test successful league unweighted fetch."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "unweighted": {
                "strikeout_rate": 0.23,
                "walk_rate": 0.08,
                "isolated_power": 0.16,
                "on_base_percentage": 0.315,
                "base_running": 0.0
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = repo._get_league_unweighted_blocking()
        
        assert result["strikeout_rate"] == 0.23
        assert result["walk_rate"] == 0.08


class TestRosterRepositoryGetLeagueUnweightedAverageAsync:
    """Tests for get_league_unweighted_average async method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.roster_repository.to_thread')
    async def test_get_league_unweighted_average_loads_and_caches(self, mock_to_thread):
        """Test that league average is loaded and cached."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        # Mock the blocking call
        mock_to_thread.run_sync = AsyncMock(return_value={
            "strikeout_rate": 0.23,
            "walk_rate": 0.08,
            "isolated_power": 0.16,
            "on_base_percentage": 0.315,
            "base_running": 0.0
        })
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_league_unweighted_average()
        
        assert result["strikeout_rate"] == 0.23
        assert repo._league_avg_cache is not None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_average_exception_handling(self):
        """Test exception handling in get_league_unweighted_average."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_average()
        
        assert exc_info.value.status_code == 500


class TestRosterRepositoryGetLeagueUnweightedStdBlocking:
    """Tests for _get_league_unweighted_std_blocking method."""
    
    @pytest.mark.unit
    def test_get_league_unweighted_std_blocking_not_found(self):
        """Test when league document not found."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_std_blocking()
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    def test_get_league_unweighted_std_blocking_malformed(self):
        """Test when std data is malformed."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"unweighted_std": "not_a_dict"}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_std_blocking()
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    def test_get_league_unweighted_std_blocking_missing_keys(self):
        """Test when required keys are missing."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "unweighted_std": {
                "strikeout_rate": 0.02,
                # Missing other keys
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_unweighted_std_blocking()
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    def test_get_league_unweighted_std_blocking_success(self):
        """Test successful std fetch."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "unweighted_std": {
                "strikeout_rate": 0.02,
                "walk_rate": 0.01,
                "isolated_power": 0.03,
                "on_base_percentage": 0.015,
                "base_running": 0.5
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = repo._get_league_unweighted_std_blocking()
        
        assert result["strikeout_rate"] == 0.02


class TestRosterRepositoryGetLeagueUnweightedStdAsync:
    """Tests for get_league_unweighted_std async method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.roster_repository.to_thread')
    async def test_get_league_unweighted_std_loads_and_caches(self, mock_to_thread):
        """Test that league std is loaded and cached."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        mock_to_thread.run_sync = AsyncMock(return_value={
            "strikeout_rate": 0.02,
            "walk_rate": 0.01,
            "isolated_power": 0.03,
            "on_base_percentage": 0.015,
            "base_running": 0.5
        })
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_league_unweighted_std()
        
        assert result["strikeout_rate"] == 0.02
        assert repo._league_std_cache is not None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_std_exception_handling(self):
        """Test exception handling in get_league_unweighted_std."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_std()
        
        assert exc_info.value.status_code == 500


class TestRosterRepositoryGetLeagueWeightedStdBlocking:
    """Tests for _get_league_weighted_std_blocking method."""
    
    @pytest.mark.unit
    def test_get_league_weighted_std_blocking_not_found(self):
        """Test when league document not found."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_weighted_std_blocking()
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    def test_get_league_weighted_std_blocking_malformed(self):
        """Test when weighted std data is malformed."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"weighted_by_player_count_std": "not_a_dict"}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_weighted_std_blocking()
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    def test_get_league_weighted_std_blocking_success(self):
        """Test successful weighted std fetch."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "weighted_by_player_count_std": {
                "strikeout_rate": 0.025,
                "walk_rate": 0.012,
                "isolated_power": 0.032,
                "on_base_percentage": 0.018,
                "base_running": 0.6
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = repo._get_league_weighted_std_blocking()
        
        assert result["strikeout_rate"] == 0.025


class TestRosterRepositoryGetLeagueWeightedStdAsync:
    """Tests for get_league_weighted_std async method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.roster_repository.to_thread')
    async def test_get_league_weighted_std_success(self, mock_to_thread):
        """Test successful weighted std fetch."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        mock_to_thread.run_sync = AsyncMock(return_value={
            "strikeout_rate": 0.025,
            "walk_rate": 0.012,
            "isolated_power": 0.032,
            "on_base_percentage": 0.018,
            "base_running": 0.6
        })
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        result = await repo.get_league_weighted_std()
        
        assert result["strikeout_rate"] == 0.025
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_weighted_std_exception_handling(self):
        """Test exception handling in get_league_weighted_std."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_weighted_std()
        
        assert exc_info.value.status_code == 500


class TestRosterRepositoryFetchTeamRoster:
    """Tests for fetch_team_roster method."""
    
    @pytest.mark.unit
    @patch('infrastructure.roster_repository.requests')
    def test_fetch_team_roster_success(self, mock_requests):
        """Test successful team roster fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {"roster": [{"player": "data"}]}
        mock_requests.get.return_value = mock_response
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(Mock(), mock_player_repo)
        
        result = repo.fetch_team_roster(147, 2023)
        
        assert result == {"roster": [{"player": "data"}]}
    
    @pytest.mark.unit
    @patch('infrastructure.roster_repository.requests')
    def test_fetch_team_roster_exception(self, mock_requests):
        """Test fetch_team_roster handles exceptions."""
        mock_requests.get.side_effect = Exception("Network error")
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(Mock(), mock_player_repo)
        
        result = repo.fetch_team_roster(147, 2023)
        
        assert result == {}


class TestRosterRepositoryGetPlayersDataException:
    """Tests for get_players_seasons_data exception handling."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_players_seasons_data_general_exception(self):
        """Test general exception handling in get_players_seasons_data."""
        mock_db = Mock()
        mock_player_repo = Mock()
        mock_player_repo._ensure_cache_loaded = AsyncMock(side_effect=Exception("Cache error"))
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_players_seasons_data([12345])
        
        assert exc_info.value.status_code == 500
        assert "Failed to get players seasons data" in exc_info.value.detail


class TestRosterRepositoryGetLeagueAverageDoubleCheck:
    """Tests for double-check locking in get_league_unweighted_average."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_average_double_check(self):
        """Test double-check locking when cache loaded after lock."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        # Pre-populate cache
        repo._league_avg_cache = {"strikeout_rate": 0.23}
        
        # Should return cached value without calling DB
        result = await repo.get_league_unweighted_average()
        
        assert result["strikeout_rate"] == 0.23
        mock_db.collection.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_average_http_exception_reraise(self):
        """Test that HTTPException is re-raised."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_average()
        
        assert exc_info.value.status_code == 404


class TestRosterRepositoryGetLeagueStdDoubleCheck:
    """Tests for double-check locking in get_league_unweighted_std."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_std_double_check(self):
        """Test double-check locking when cache loaded after lock."""
        mock_db = Mock()
        mock_player_repo = Mock()
        
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        # Pre-populate cache
        repo._league_std_cache = {"strikeout_rate": 0.02}
        
        # Should return cached value without calling DB
        result = await repo.get_league_unweighted_std()
        
        assert result["strikeout_rate"] == 0.02
        mock_db.collection.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_unweighted_std_http_exception_reraise(self):
        """Test that HTTPException is re-raised."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_unweighted_std()
        
        assert exc_info.value.status_code == 404


class TestRosterRepositoryGetLeagueWeightedStdMissingKeys:
    """Tests for missing keys in weighted std."""
    
    @pytest.mark.unit
    def test_get_league_weighted_std_blocking_missing_keys(self):
        """Test when required keys are missing in weighted std."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "weighted_by_player_count_std": {
                "strikeout_rate": 0.025,
                # Missing other keys
            }
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            repo._get_league_weighted_std_blocking()
        
        assert exc_info.value.status_code == 500
        assert "missing or non-numeric" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_league_weighted_std_http_exception_reraise(self):
        """Test that HTTPException is re-raised in get_league_weighted_std."""
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        mock_player_repo = Mock()
        repo = RosterRepositoryFirebase(mock_db, mock_player_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_league_weighted_std()
        
        assert exc_info.value.status_code == 404
