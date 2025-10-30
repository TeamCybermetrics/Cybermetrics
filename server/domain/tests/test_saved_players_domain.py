import pytest
from fastapi import HTTPException, status
from domain.saved_players_domain import SavedPlayersDomain


class TestSavedPlayersDomain:
    """Unit tests for SavedPlayersDomain business logic"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.saved_players_domain = SavedPlayersDomain()
    
    # Test validate_player_info
    def test_validate_player_info_valid_int_id(self):
        """Test validation passes with valid integer player ID"""
        player_info = {"id": 12345, "name": "Test Player"}
        result = self.saved_players_domain.validate_player_info(player_info)
        assert result == "12345"
    
    def test_validate_player_info_valid_string_id(self):
        """Test validation passes with valid string player ID"""
        player_info = {"id": "12345", "name": "Test Player"}
        result = self.saved_players_domain.validate_player_info(player_info)
        assert result == "12345"
    
    def test_validate_player_info_missing_id(self):
        """Test validation fails when ID is missing"""
        player_info = {"name": "Test Player"}
        with pytest.raises(HTTPException) as exc_info:
            self.saved_players_domain.validate_player_info(player_info)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player ID is required" in str(exc_info.value.detail)
    
    def test_validate_player_info_none_id(self):
        """Test validation fails when ID is None"""
        player_info = {"id": None, "name": "Test Player"}
        with pytest.raises(HTTPException) as exc_info:
            self.saved_players_domain.validate_player_info(player_info)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player ID is required" in str(exc_info.value.detail)
    
    def test_validate_player_info_empty_string_id(self):
        """Test validation fails when ID is empty string"""
        player_info = {"id": "", "name": "Test Player"}
        with pytest.raises(HTTPException) as exc_info:
            self.saved_players_domain.validate_player_info(player_info)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player ID is required" in str(exc_info.value.detail)
    
    def test_validate_player_info_whitespace_id(self):
        """Test validation fails when ID is only whitespace"""
        player_info = {"id": "   ", "name": "Test Player"}
        with pytest.raises(HTTPException) as exc_info:
            self.saved_players_domain.validate_player_info(player_info)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Player ID is required" in str(exc_info.value.detail)
    
    def test_validate_player_info_strips_whitespace(self):
        """Test validation strips whitespace from ID"""
        player_info = {"id": "  12345  ", "name": "Test Player"}
        result = self.saved_players_domain.validate_player_info(player_info)
        assert result == "12345"
    
    def test_validate_player_info_zero_id(self):
        """Test validation accepts zero as valid ID"""
        player_info = {"id": 0, "name": "Test Player"}
        result = self.saved_players_domain.validate_player_info(player_info)
        assert result == "0"
