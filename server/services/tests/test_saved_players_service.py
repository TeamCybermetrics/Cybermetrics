import pytest
from unittest.mock import AsyncMock, Mock
from services.saved_players_service import SavedPlayersService
from models.players import AddPlayerResponse, DeletePlayerResponse, SavedPlayer


class TestSavedPlayersService:
    """Unit tests for SavedPlayersService"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_saved_players_repository = Mock()
        self.mock_saved_players_domain = Mock()
        self.saved_players_service = SavedPlayersService(
            saved_players_repository=self.mock_saved_players_repository,
            saved_players_domain=self.mock_saved_players_domain
        )
    
    # Test add_player
    @pytest.mark.asyncio
    async def test_add_player_success(self):
        """Test successfully adding a player"""
        user_id = "user123"
        player_info = {
            "id": 545361,
            "name": "Mike Trout",
            "team": "LAA"
        }
        
        # Mock domain validation
        self.mock_saved_players_domain.validate_player_info.return_value = "545361"
        
        # Mock repository response
        expected_response = AddPlayerResponse(
            message="Player added successfully",
            player_id="545361"
        )
        self.mock_saved_players_repository.add_player = AsyncMock(return_value=expected_response)
        
        result = await self.saved_players_service.add_player(user_id, player_info)
        
        # Verify domain validation was called
        self.mock_saved_players_domain.validate_player_info.assert_called_once_with(player_info)
        
        # Verify repository was called
        self.mock_saved_players_repository.add_player.assert_called_once_with(
            user_id, player_info, "545361"
        )
        
        # Verify response
        assert result == expected_response
        assert result.player_id == "545361"
    
    @pytest.mark.asyncio
    async def test_add_player_invalid_info(self):
        """Test adding player with invalid info"""
        user_id = "user123"
        player_info = {"name": "Mike Trout"}  # Missing ID
        
        # Mock domain validation to raise exception
        from fastapi import HTTPException, status
        self.mock_saved_players_domain.validate_player_info.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player ID is required"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.saved_players_service.add_player(user_id, player_info)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify repository was not called
        self.mock_saved_players_repository.add_player.assert_not_called()
    
    # Test get_all_players
    @pytest.mark.asyncio
    async def test_get_all_players_success(self):
        """Test successfully retrieving all saved players"""
        user_id = "user123"
        
        # Mock repository response
        expected_players = [
            SavedPlayer(
                id="545361",
                name="Mike Trout",
                team="LAA",
                position="OF"
            ),
            SavedPlayer(
                id="660271",
                name="Shohei Ohtani",
                team="LAD",
                position="DH"
            )
        ]
        self.mock_saved_players_repository.get_all_players = AsyncMock(
            return_value=expected_players
        )
        
        result = await self.saved_players_service.get_all_players(user_id)
        
        # Verify repository was called
        self.mock_saved_players_repository.get_all_players.assert_called_once_with(user_id)
        
        # Verify response
        assert result == expected_players
        assert len(result) == 2
        assert result[0].name == "Mike Trout"
    
    @pytest.mark.asyncio
    async def test_get_all_players_empty(self):
        """Test retrieving all players when user has none saved"""
        user_id = "user123"
        
        # Mock repository response
        self.mock_saved_players_repository.get_all_players = AsyncMock(return_value=[])
        
        result = await self.saved_players_service.get_all_players(user_id)
        
        # Verify response is empty
        assert result == []
    
    # Test get_player
    @pytest.mark.asyncio
    async def test_get_player_success(self):
        """Test successfully retrieving a specific saved player"""
        user_id = "user123"
        player_id = "545361"
        
        # Mock repository response
        expected_player = SavedPlayer(
            id="545361",
            name="Mike Trout",
            team="LAA",
            position="OF"
        )
        self.mock_saved_players_repository.get_player = AsyncMock(
            return_value=expected_player
        )
        
        result = await self.saved_players_service.get_player(user_id, player_id)
        
        # Verify repository was called
        self.mock_saved_players_repository.get_player.assert_called_once_with(
            user_id, player_id
        )
        
        # Verify response
        assert result == expected_player
        assert result.name == "Mike Trout"
    
    @pytest.mark.asyncio
    async def test_get_player_not_found(self):
        """Test retrieving a player that doesn't exist"""
        user_id = "user123"
        player_id = "999999"
        
        # Mock repository to raise exception
        from fastapi import HTTPException, status
        self.mock_saved_players_repository.get_player = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.saved_players_service.get_player(user_id, player_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    # Test delete_player
    @pytest.mark.asyncio
    async def test_delete_player_success(self):
        """Test successfully deleting a saved player"""
        user_id = "user123"
        player_id = "545361"
        
        # Mock repository response
        expected_response = DeletePlayerResponse(
            message="Player deleted successfully"
        )
        self.mock_saved_players_repository.delete_player = AsyncMock(
            return_value=expected_response
        )
        
        result = await self.saved_players_service.delete_player(user_id, player_id)
        
        # Verify repository was called
        self.mock_saved_players_repository.delete_player.assert_called_once_with(
            user_id, player_id
        )
        
        # Verify response
        assert result == expected_response
        assert result.message == "Player deleted successfully"
    
    @pytest.mark.asyncio
    async def test_delete_player_not_found(self):
        """Test deleting a player that doesn't exist"""
        user_id = "user123"
        player_id = "999999"
        
        # Mock repository to raise exception
        from fastapi import HTTPException, status
        self.mock_saved_players_repository.delete_player = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.saved_players_service.delete_player(user_id, player_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
