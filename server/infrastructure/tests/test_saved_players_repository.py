"""
Unit tests for SavedPlayersRepositoryFirebase with mocked Firebase.
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from fastapi import HTTPException
from infrastructure.saved_players_repository import SavedPlayersRepositoryFirebase
from entities.players import SavedPlayer
from dtos.saved_player_dtos import AddPlayerResponse, DeletePlayerResponse


class TestSavedPlayersRepositoryInitialization:
    """Tests for repository initialization."""
    
    @pytest.mark.unit
    def test_repository_initialization(self):
        """Test that repository initializes with database."""
        mock_db = Mock()
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        assert repo.db is mock_db
        assert repo._logger is not None


class TestSavedPlayersRepositoryAddPlayer:
    """Tests for add_player method."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock Firestore database."""
        db = Mock()
        collection_mock = Mock()
        document_mock = Mock()
        subcollection_mock = Mock()
        subdocument_mock = Mock()
        
        # Chain the mocks: db.collection().document().collection().document().set()
        db.collection.return_value = collection_mock
        collection_mock.document.return_value = document_mock
        document_mock.collection.return_value = subcollection_mock
        subcollection_mock.document.return_value = subdocument_mock
        subdocument_mock.set = Mock()
        
        return db
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_success(self, mock_db):
        """Test successful player addition."""
        repo = SavedPlayersRepositoryFirebase(mock_db)
        player_info = {"id": 12345, "name": "Test Player"}
        
        result = await repo.add_player("user123", player_info, "12345")
        
        assert isinstance(result, AddPlayerResponse)
        assert result.player_id == "12345"
        assert "successfully" in result.message
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_no_db(self):
        """Test add_player raises error when database is None."""
        repo = SavedPlayersRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.add_player("user123", {}, "12345")
        
        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_firestore_error(self, mock_db):
        """Test add_player handles Firestore errors."""
        # Make the set() method raise an exception
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.set.side_effect = Exception("Firestore error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.add_player("user123", {}, "12345")
        
        assert exc_info.value.status_code == 500


class TestSavedPlayersRepositoryGetAllPlayers:
    """Tests for get_all_players method."""
    
    @pytest.fixture
    def mock_db_with_players(self):
        """Create a mock database with player documents."""
        db = Mock()
        
        # Create mock player documents
        player1_doc = Mock()
        player1_doc.to_dict.return_value = {"id": 1, "name": "Player 1"}
        
        player2_doc = Mock()
        player2_doc.to_dict.return_value = {"id": 2, "name": "Player 2"}
        
        # Mock the stream() method to return player documents
        collection_mock = Mock()
        document_mock = Mock()
        subcollection_mock = Mock()
        
        db.collection.return_value = collection_mock
        collection_mock.document.return_value = document_mock
        document_mock.collection.return_value = subcollection_mock
        subcollection_mock.stream.return_value = [player1_doc, player2_doc]
        
        return db
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_success(self, mock_db_with_players):
        """Test successful retrieval of all players."""
        repo = SavedPlayersRepositoryFirebase(mock_db_with_players)
        
        result = await repo.get_all_players("user123")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(p, SavedPlayer) for p in result)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_empty(self):
        """Test get_all_players with no saved players."""
        db = Mock()
        db.collection.return_value.document.return_value.collection.return_value.stream.return_value = []
        
        repo = SavedPlayersRepositoryFirebase(db)
        result = await repo.get_all_players("user123")
        
        assert result == []
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_no_db(self):
        """Test get_all_players raises error when database is None."""
        repo = SavedPlayersRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_all_players("user123")
        
        assert exc_info.value.status_code == 503


class TestSavedPlayersRepositoryGetPlayer:
    """Tests for get_player method."""
    
    @pytest.fixture
    def mock_db_with_player(self):
        """Create a mock database with a single player."""
        db = Mock()
        
        player_doc = Mock()
        player_doc.exists = True
        player_doc.to_dict.return_value = {"id": 1, "name": "Test Player"}
        
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = player_doc
        
        return db
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_success(self, mock_db_with_player):
        """Test successful retrieval of a single player."""
        repo = SavedPlayersRepositoryFirebase(mock_db_with_player)
        
        result = await repo.get_player("user123", "player456")
        
        assert isinstance(result, SavedPlayer)
        assert result.name == "Test Player"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_not_found(self):
        """Test get_player when player doesn't exist."""
        db = Mock()
        player_doc = Mock()
        player_doc.exists = False
        
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = player_doc
        
        repo = SavedPlayersRepositoryFirebase(db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_player("user123", "player456")
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_no_db(self):
        """Test get_player raises error when database is None."""
        repo = SavedPlayersRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_player("user123", "player456")
        
        assert exc_info.value.status_code == 503


class TestSavedPlayersRepositoryDeletePlayer:
    """Tests for delete_player method."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock Firestore database."""
        db = Mock()
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete = Mock()
        return db
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_success(self, mock_db):
        """Test successful player deletion."""
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        result = await repo.delete_player("user123", "player456")
        
        assert isinstance(result, DeletePlayerResponse)
        assert "successfully" in result.message
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_no_db(self):
        """Test delete_player raises error when database is None."""
        repo = SavedPlayersRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.delete_player("user123", "player456")
        
        assert exc_info.value.status_code == 503
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_firestore_error(self, mock_db):
        """Test delete_player handles Firestore errors."""
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete.side_effect = Exception("Firestore error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.delete_player("user123", "player456")
        
        assert exc_info.value.status_code == 500


class TestSavedPlayersRepositoryUpdatePosition:
    """Tests for update_position method."""
    
    @pytest.fixture
    def mock_db_with_player(self):
        """Create a mock database with a player."""
        db = Mock()
        
        player_doc = Mock()
        player_doc.exists = True
        player_doc.to_dict.return_value = {"id": 1, "name": "Test Player", "position": "P"}
        
        document_ref = Mock()
        document_ref.get.return_value = player_doc
        document_ref.update = Mock()
        
        db.collection.return_value.document.return_value.collection.return_value.document.return_value = document_ref
        
        return db
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_success(self, mock_db_with_player):
        """Test successful position update."""
        repo = SavedPlayersRepositoryFirebase(mock_db_with_player)
        
        result = await repo.update_position("user123", "player456", "SS")
        
        assert isinstance(result, SavedPlayer)
        assert result.position == "SS"  # Returns the updated position
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_clear(self, mock_db_with_player):
        """Test clearing position (setting to None)."""
        repo = SavedPlayersRepositoryFirebase(mock_db_with_player)
        
        result = await repo.update_position("user123", "player456", None)
        
        assert isinstance(result, SavedPlayer)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_player_not_found(self):
        """Test update_position when player doesn't exist."""
        db = Mock()
        player_doc = Mock()
        player_doc.exists = False
        
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = player_doc
        
        repo = SavedPlayersRepositoryFirebase(db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.update_position("user123", "player456", "P")
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_no_db(self):
        """Test update_position raises error when database is None."""
        repo = SavedPlayersRepositoryFirebase(None)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.update_position("user123", "player456", "P")
        
        assert exc_info.value.status_code == 503


class TestSavedPlayersRepositoryErrorHandling:
    """Tests for error handling in various methods."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_general_exception(self):
        """Test add_player handles general exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.set.side_effect = Exception("Unexpected error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.add_player("user123", {}, "player456")
        
        assert exc_info.value.status_code == 500
        assert "Failed to add player" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_exception(self):
        """Test get_all_players handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.stream.side_effect = Exception("DB error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_all_players("user123")
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_exception(self):
        """Test get_player handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.get_player("user123", "player456")
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_exception(self):
        """Test delete_player handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete.side_effect = Exception("DB error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.delete_player("user123", "player456")
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_exception(self):
        """Test update_position handles exceptions."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.side_effect = Exception("DB error")
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.update_position("user123", "player456", "P")
        
        assert exc_info.value.status_code == 500


class TestSavedPlayersRepositoryHTTPExceptionReRaise:
    """Tests for HTTPException re-raising."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_http_exception_reraise(self):
        """Test that HTTPException is re-raised in add_player."""
        mock_db = Mock()
        
        # Create a function that raises HTTPException
        def raise_http_exception(*args, **kwargs):
            raise HTTPException(status_code=400, detail="Test error")
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.set = raise_http_exception
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.add_player("user123", {}, "player456")
        
        # Should re-raise the original HTTPException
        assert exc_info.value.status_code == 400
        assert "Test error" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_http_exception_reraise(self):
        """Test that HTTPException is re-raised in delete_player."""
        mock_db = Mock()
        
        # Create a function that raises HTTPException
        def raise_http_exception(*args, **kwargs):
            raise HTTPException(status_code=404, detail="Player not found")
        
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete = raise_http_exception
        
        repo = SavedPlayersRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.delete_player("user123", "player456")
        
        # Should re-raise the original HTTPException
        assert exc_info.value.status_code == 404
        assert "Player not found" in exc_info.value.detail
