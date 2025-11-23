"""
Unit tests for PlayerRepositoryFirebase with mocked Firebase.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from infrastructure.player_repository import PlayerRepositoryFirebase


class TestPlayerRepositoryInitialization:
    """Tests for PlayerRepositoryFirebase initialization."""
    
    @pytest.mark.unit
    def test_repository_initialization(self):
        """Test that repository initializes with database."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        assert repo.db is mock_db
        assert repo._players_cache == []
        assert repo._cache_loaded is False


class TestPlayerRepositoryLoadDatabase:
    """Tests for database loading methods."""
    
    @pytest.mark.unit
    def test_load_database_blocking(self):
        """Test blocking database load."""
        mock_db = Mock()
        
        # Create mock player documents
        player1_doc = Mock()
        player1_doc.to_dict.return_value = {"mlbam_id": 12345, "name": "Player 1"}
        
        player2_doc = Mock()
        player2_doc.to_dict.return_value = {"mlbam_id": 67890, "name": "Player 2"}
        
        mock_db.collection.return_value.stream.return_value = [player1_doc, player2_doc]
        
        repo = PlayerRepositoryFirebase(mock_db)
        count = repo._load_database_blocking()
        
        assert count == 2
        assert repo._cache_loaded is True
        assert len(repo._players_cache) == 2
        assert 12345 in repo._players_cache_by_id
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ensure_cache_loaded_already_loaded(self):
        """Test that cache loading is skipped if already loaded."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        repo._cache_loaded = True
        
        await repo._ensure_cache_loaded()
        
        # Should not call database
        mock_db.collection.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ensure_cache_loaded_no_db(self):
        """Test cache loading with no database."""
        repo = PlayerRepositoryFirebase(None)
        
        await repo._ensure_cache_loaded()
        
        # Should not raise error
        assert repo._cache_loaded is False


class TestPlayerRepositoryGetAllPlayers:
    """Tests for get_all_players method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_returns_cache(self):
        """Test that get_all_players returns cached players."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        # Pre-populate cache
        repo._players_cache = [
            {"mlbam_id": 12345, "name": "Player 1"},
            {"mlbam_id": 67890, "name": "Player 2"}
        ]
        repo._cache_loaded = True
        
        result = await repo.get_all_players()
        
        assert len(result) == 2
        assert result[0]["name"] == "Player 1"


class TestPlayerRepositoryGetPlayerById:
    """Tests for get_player_by_id method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_by_id_found(self):
        """Test getting player by ID when found in cache."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        # Pre-populate cache
        repo._players_cache_by_id = {
            12345: {"mlbam_id": 12345, "name": "Test Player"}
        }
        repo._cache_loaded = True
        
        result = await repo.get_player_by_id(12345)
        
        assert result is not None
        assert result["name"] == "Test Player"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_by_id_not_found(self):
        """Test getting player by ID when not found returns None."""
        mock_db = Mock()
        
        # Mock the blocking call to return None
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        repo = PlayerRepositoryFirebase(mock_db)
        repo._cache_loaded = True
        repo._players_cache_by_id = {}
        
        result = await repo.get_player_by_id(99999)
        
        assert result is None


class TestPlayerRepositoryBuildPlayerImageUrl:
    """Tests for build_player_image_url method."""
    
    @pytest.mark.unit
    def test_build_player_image_url(self):
        """Test building player image URL."""
        repo = PlayerRepositoryFirebase(Mock())
        
        url = repo.build_player_image_url(12345)
        
        assert "12345" in url
        assert url.startswith("https://")


class TestPlayerRepositoryLoadDatabaseError:
    """Tests for database loading error handling."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ensure_cache_loaded_error(self):
        """Test cache loading handles errors."""
        mock_db = Mock()
        mock_db.collection.return_value.stream.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo._ensure_cache_loaded()
        
        assert exc_info.value.status_code == 500


class TestPlayerRepositoryGetPlayerByIdCaching:
    """Tests for get_player_by_id caching behavior."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_by_id_adds_to_cache(self):
        """Test that fetched player is added to cache."""
        mock_db = Mock()
        
        # Mock document fetch
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"mlbam_id": 12345, "name": "New Player"}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        repo = PlayerRepositoryFirebase(mock_db)
        repo._cache_loaded = True
        repo._players_cache_by_id = {}
        repo._players_cache = []
        
        result = await repo.get_player_by_id(12345)
        
        assert result is not None
        assert 12345 in repo._players_cache_by_id
        assert len(repo._players_cache) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_by_id_exception_handling(self):
        """Test get_player_by_id handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        repo._cache_loaded = True
        repo._players_cache_by_id = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_player_by_id(12345)
        
        assert exc_info.value.status_code == 500


class TestPlayerRepositoryGetAllPlayersNoDb:
    """Tests for get_all_players without database."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_no_db(self):
        """Test get_all_players raises error when database is None."""
        repo = PlayerRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_all_players()
        
        assert exc_info.value.status_code == 503


class TestPlayerRepositoryGetPlayerByIdNoDb:
    """Tests for get_player_by_id without database."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_by_id_no_db(self):
        """Test get_player_by_id raises error when database is None."""
        repo = PlayerRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_player_by_id(12345)
        
        assert exc_info.value.status_code == 503


class TestPlayerRepositoryLoadDatabaseBlocking:
    """Tests for _load_database_blocking method."""
    
    @pytest.mark.unit
    def test_load_database_blocking_with_invalid_mlbam_id(self):
        """Test loading database with invalid mlbam_id values."""
        mock_db = Mock()
        
        player1_doc = Mock()
        player1_doc.to_dict.return_value = {"mlbam_id": 12345, "name": "Player 1"}
        
        player2_doc = Mock()
        player2_doc.to_dict.return_value = {"mlbam_id": "invalid", "name": "Player 2"}
        
        player3_doc = Mock()
        player3_doc.to_dict.return_value = {"mlbam_id": None, "name": "Player 3"}
        
        mock_db.collection.return_value.stream.return_value = [player1_doc, player2_doc, player3_doc]
        
        repo = PlayerRepositoryFirebase(mock_db)
        count = repo._load_database_blocking()
        
        assert count == 3
        assert len(repo._players_cache_by_id) == 1
        assert 12345 in repo._players_cache_by_id


class TestPlayerRepositoryUploadTeam:
    """Tests for upload_team method."""
    
    @pytest.mark.unit
    def test_upload_team_no_db(self):
        """Test upload_team raises error when database is None."""
        repo = PlayerRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            repo.upload_team("NYY", "New York Yankees", [{"id": 1}])
        
        assert exc_info.value.status_code == 503
    
    @pytest.mark.unit
    def test_upload_team_with_players(self):
        """Test upload_team with players."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        players = [{"id": 1, "name": "Player 1"}]
        repo.upload_team("nyy", "New York Yankees", players)
        
        mock_db.collection.assert_called_with("teams")
        mock_db.collection.return_value.document.assert_called_with("NYY")
    
    @pytest.mark.unit
    def test_upload_team_empty_players(self):
        """Test upload_team with empty players list."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        result = repo.upload_team("nyy", "New York Yankees", [])
        
        assert result is None
        mock_db.collection.assert_not_called()


class TestPlayerRepositoryBulkUpsertPlayers:
    """Tests for bulk_upsert_players method."""
    
    @pytest.mark.unit
    def test_bulk_upsert_players_empty_list(self):
        """Test bulk_upsert_players with empty list."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        repo.bulk_upsert_players([])
        
        mock_db.batch.assert_not_called()
    
    @pytest.mark.unit
    def test_bulk_upsert_players_with_data(self):
        """Test bulk_upsert_players with player data."""
        mock_db = Mock()
        mock_batch = Mock()
        mock_db.batch.return_value = mock_batch
        
        repo = PlayerRepositoryFirebase(mock_db)
        
        players = [
            {"mlbam_id": 12345, "name": "Player 1"},
            {"mlbam_id": 67890, "name": "Player 2"}
        ]
        
        repo.bulk_upsert_players(players)
        
        assert mock_batch.set.call_count == 2
        mock_batch.commit.assert_called_once()


class TestPlayerRepositoryListTeamIds:
    """Tests for list_team_ids method."""
    
    @pytest.mark.unit
    def test_list_team_ids_no_db(self):
        """Test list_team_ids with no database."""
        repo = PlayerRepositoryFirebase(None)
        
        result = repo.list_team_ids()
        
        assert result == []
    
    @pytest.mark.unit
    def test_list_team_ids_success(self):
        """Test list_team_ids returns team IDs."""
        mock_db = Mock()
        mock_doc1 = Mock()
        mock_doc1.id = "NYY"
        mock_doc2 = Mock()
        mock_doc2.id = "BOS"
        
        mock_db.collection.return_value.list_documents.return_value = [mock_doc1, mock_doc2]
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.list_team_ids()
        
        assert result == ["NYY", "BOS"]
    
    @pytest.mark.unit
    def test_list_team_ids_exception(self):
        """Test list_team_ids handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.list_documents.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.list_team_ids()
        
        assert result == []


class TestPlayerRepositoryGetTeamPositionalPlayers:
    """Tests for get_team_positional_players method."""
    
    @pytest.mark.unit
    def test_get_team_positional_players_no_db(self):
        """Test get_team_positional_players with no database."""
        repo = PlayerRepositoryFirebase(None)
        
        result = repo.get_team_positional_players("NYY")
        
        assert result == []
    
    @pytest.mark.unit
    def test_get_team_positional_players_not_found(self):
        """Test get_team_positional_players when team not found."""
        mock_db = Mock()
        mock_snap = Mock()
        mock_snap.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_snap
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.get_team_positional_players("NYY")
        
        assert result == []
    
    @pytest.mark.unit
    def test_get_team_positional_players_success(self):
        """Test get_team_positional_players returns players."""
        mock_db = Mock()
        mock_snap = Mock()
        mock_snap.exists = True
        mock_snap.to_dict.return_value = {"positional_players": [{"id": 1}]}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_snap
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.get_team_positional_players("NYY")
        
        assert result == [{"id": 1}]
    
    @pytest.mark.unit
    def test_get_team_positional_players_exception(self):
        """Test get_team_positional_players handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.get_team_positional_players("NYY")
        
        assert result == []


class TestPlayerRepositorySetTeamRosterAverage:
    """Tests for set_team_roster_average method."""
    
    @pytest.mark.unit
    def test_set_team_roster_average_no_db(self):
        """Test set_team_roster_average with no database."""
        repo = PlayerRepositoryFirebase(None)
        
        result = repo.set_team_roster_average("NYY", {"avg": 0.250})
        
        assert result is None
    
    @pytest.mark.unit
    def test_set_team_roster_average_success(self):
        """Test set_team_roster_average sets data."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        repo.set_team_roster_average("NYY", {"avg": 0.250})
        
        mock_db.collection.assert_called_with("teams")
    
    @pytest.mark.unit
    def test_set_team_roster_average_exception(self):
        """Test set_team_roster_average handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.set.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.set_team_roster_average("NYY", {"avg": 0.250})
        
        assert result is None


class TestPlayerRepositorySetLeagueAverages:
    """Tests for set_league_averages method."""
    
    @pytest.mark.unit
    def test_set_league_averages_no_db(self):
        """Test set_league_averages with no database."""
        repo = PlayerRepositoryFirebase(None)
        
        result = repo.set_league_averages({"avg": 0.250})
        
        assert result is None
    
    @pytest.mark.unit
    def test_set_league_averages_success(self):
        """Test set_league_averages sets data."""
        mock_db = Mock()
        repo = PlayerRepositoryFirebase(mock_db)
        
        repo.set_league_averages({"avg": 0.250})
        
        mock_db.collection.assert_called_with("league")
    
    @pytest.mark.unit
    def test_set_league_averages_exception(self):
        """Test set_league_averages handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.set.side_effect = Exception("DB error")
        
        repo = PlayerRepositoryFirebase(mock_db)
        result = repo.set_league_averages({"avg": 0.250})
        
        assert result is None


class TestPlayerRepositoryBuildPlayerImageUrlEdgeCases:
    """Tests for build_player_image_url edge cases."""
    
    @pytest.mark.unit
    def test_build_player_image_url_invalid_id(self):
        """Test build_player_image_url with invalid player ID."""
        repo = PlayerRepositoryFirebase(Mock())
        
        url = repo.build_player_image_url(0)
        
        assert "people/0/headshot" in url
    
    @pytest.mark.unit
    def test_build_player_image_url_negative_id(self):
        """Test build_player_image_url with negative player ID."""
        repo = PlayerRepositoryFirebase(Mock())
        
        url = repo.build_player_image_url(-1)
        
        assert "people/0/headshot" in url


class TestPlayerRepositoryFetchTeamRoster:
    """Tests for fetch_team_roster method."""
    
    @pytest.mark.unit
    @patch('infrastructure.player_repository.requests')
    def test_fetch_team_roster_success(self, mock_requests):
        """Test fetch_team_roster returns data."""
        mock_response = Mock()
        mock_response.json.return_value = {"roster": []}
        mock_requests.get.return_value = mock_response
        
        repo = PlayerRepositoryFirebase(Mock())
        result = repo.fetch_team_roster(147, 2023)
        
        assert result == {"roster": []}
    
    @pytest.mark.unit
    @patch('infrastructure.player_repository.requests')
    def test_fetch_team_roster_exception(self, mock_requests):
        """Test fetch_team_roster handles exceptions."""
        mock_requests.get.side_effect = Exception("Network error")
        
        repo = PlayerRepositoryFirebase(Mock())
        result = repo.fetch_team_roster(147, 2023)
        
        assert result == {}


class TestPlayerRepositoryEnsureCacheLoadedAlreadyLoaded:
    """Tests for _ensure_cache_loaded when already loaded after lock."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ensure_cache_loaded_already_loaded_after_lock(self):
        """Test double-check locking when cache loaded by another thread."""
        mock_db = Mock()
        mock_db.collection.return_value.stream.return_value = []
        
        repo = PlayerRepositoryFirebase(mock_db)
        
        # First call should load the cache
        await repo._ensure_cache_loaded()
        assert repo._cache_loaded is True
        
        # Second call should return early (double-check)
        await repo._ensure_cache_loaded()
        assert repo._cache_loaded is True


class TestPlayerRepositoryEnsureCacheLoadedLogging:
    """Tests for _ensure_cache_loaded logging."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.player_repository.to_thread')
    async def test_ensure_cache_loaded_logs_count(self, mock_to_thread):
        """Test that cache loading logs the count."""
        mock_db = Mock()
        mock_db.collection.return_value.stream.return_value = []
        
        mock_to_thread.run_sync = AsyncMock(return_value=0)
        
        repo = PlayerRepositoryFirebase(mock_db)
        
        await repo._ensure_cache_loaded()
        
        # Should have called run_sync
        mock_to_thread.run_sync.assert_called_once()
