"""
Unit tests for SavedPlayersService.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from services.saved_players_service import SavedPlayersService
from entities.players import SavedPlayer
from dtos.saved_player_dtos import AddPlayerResponse, DeletePlayerResponse


class TestSavedPlayersServiceInitialization:
    """Tests for SavedPlayersService initialization."""
    
    @pytest.mark.unit
    def test_service_initialization(self):
        """Test that service initializes with dependencies."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        service = SavedPlayersService(mock_repo, mock_domain)
        
        assert service.saved_players_repository is mock_repo
        assert service.saved_players_domain is mock_domain


class TestSavedPlayersServiceAddPlayer:
    """Tests for add_player method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = Mock()
        repo.add_player = AsyncMock(return_value=AddPlayerResponse(
            message="Player added successfully",
            player_id="12345"
        ))
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock domain."""
        domain = Mock()
        domain.validate_player_info = Mock(return_value="12345")
        return domain
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_validates_info(self, mock_repository, mock_domain):
        """Test that add_player validates player info."""
        service = SavedPlayersService(mock_repository, mock_domain)
        player_info = {"id": 12345, "name": "Test Player"}
        
        await service.add_player("user123", player_info)
        
        mock_domain.validate_player_info.assert_called_once_with(player_info)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_calls_repository(self, mock_repository, mock_domain):
        """Test that add_player calls repository with correct params."""
        service = SavedPlayersService(mock_repository, mock_domain)
        player_info = {"id": 12345, "name": "Test Player"}
        
        await service.add_player("user123", player_info)
        
        mock_repository.add_player.assert_called_once_with("user123", player_info, "12345")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_player_returns_response(self, mock_repository, mock_domain):
        """Test that add_player returns AddPlayerResponse."""
        service = SavedPlayersService(mock_repository, mock_domain)
        player_info = {"id": 12345, "name": "Test Player"}
        
        result = await service.add_player("user123", player_info)
        
        assert isinstance(result, AddPlayerResponse)
        assert result.player_id == "12345"


class TestSavedPlayersServiceGetAllPlayers:
    """Tests for get_all_players method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = Mock()
        repo.get_all_players = AsyncMock(return_value=[
            SavedPlayer(id=1, name="Player 1"),
            SavedPlayer(id=2, name="Player 2")
        ])
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock domain."""
        return Mock()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_calls_repository(self, mock_repository, mock_domain):
        """Test that get_all_players calls repository."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.get_all_players("user123")
        
        mock_repository.get_all_players.assert_called_once_with("user123")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_players_returns_list(self, mock_repository, mock_domain):
        """Test that get_all_players returns list of SavedPlayer."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        result = await service.get_all_players("user123")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(p, SavedPlayer) for p in result)


class TestSavedPlayersServiceGetPlayer:
    """Tests for get_player method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = Mock()
        repo.get_player = AsyncMock(return_value=SavedPlayer(id=1, name="Test Player"))
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock domain."""
        return Mock()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_calls_repository(self, mock_repository, mock_domain):
        """Test that get_player calls repository with correct params."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.get_player("user123", "player456")
        
        mock_repository.get_player.assert_called_once_with("user123", "player456")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_returns_saved_player(self, mock_repository, mock_domain):
        """Test that get_player returns SavedPlayer."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        result = await service.get_player("user123", "player456")
        
        assert isinstance(result, SavedPlayer)
        assert result.name == "Test Player"


class TestSavedPlayersServiceDeletePlayer:
    """Tests for delete_player method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = Mock()
        repo.delete_player = AsyncMock(return_value=DeletePlayerResponse(
            message="Player deleted successfully"
        ))
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock domain."""
        return Mock()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_calls_repository(self, mock_repository, mock_domain):
        """Test that delete_player calls repository."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.delete_player("user123", "player456")
        
        mock_repository.delete_player.assert_called_once_with("user123", "player456")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_player_returns_response(self, mock_repository, mock_domain):
        """Test that delete_player returns DeletePlayerResponse."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        result = await service.delete_player("user123", "player456")
        
        assert isinstance(result, DeletePlayerResponse)
        assert "deleted successfully" in result.message


class TestSavedPlayersServiceUpdatePosition:
    """Tests for update_player_position method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = Mock()
        repo.update_position = AsyncMock(return_value=SavedPlayer(
            id=1,
            name="Test Player",
            position="P"
        ))
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock domain."""
        domain = Mock()
        domain.validate_player_id = Mock(return_value="12345")
        domain.normalize_position = Mock(return_value="P")
        return domain
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_validates_player_id(self, mock_repository, mock_domain):
        """Test that update_player_position validates player ID."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.update_player_position("user123", "12345", "pitcher")
        
        mock_domain.validate_player_id.assert_called_once_with("12345")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_normalizes_position(self, mock_repository, mock_domain):
        """Test that update_player_position normalizes position."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.update_player_position("user123", "12345", "pitcher")
        
        mock_domain.normalize_position.assert_called_once_with("pitcher")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_calls_repository(self, mock_repository, mock_domain):
        """Test that update_player_position calls repository."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        await service.update_player_position("user123", "12345", "pitcher")
        
        mock_repository.update_position.assert_called_once_with("user123", "12345", "P")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_position_returns_saved_player(self, mock_repository, mock_domain):
        """Test that update_player_position returns SavedPlayer."""
        service = SavedPlayersService(mock_repository, mock_domain)
        
        result = await service.update_player_position("user123", "12345", "pitcher")
        
        assert isinstance(result, SavedPlayer)
        assert result.position == "P"
