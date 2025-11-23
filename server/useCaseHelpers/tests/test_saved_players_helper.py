"""
Unit tests for SavedPlayersDomain helper class.
"""
import pytest
from useCaseHelpers.saved_players_helper import SavedPlayersDomain
from useCaseHelpers.errors import InputValidationError


class TestSavedPlayersDomainValidatePlayerId:
    """Tests for validate_player_id method."""
    
    @pytest.fixture
    def domain(self):
        """Create a SavedPlayersDomain instance for testing."""
        return SavedPlayersDomain()
    
    @pytest.mark.unit
    def test_validate_player_id_valid_string(self, domain):
        """Test that valid string player ID is returned."""
        result = domain.validate_player_id("12345")
        assert result == "12345"
    
    @pytest.mark.unit
    def test_validate_player_id_valid_integer(self, domain):
        """Test that integer player ID is converted to string."""
        result = domain.validate_player_id(12345)
        assert result == "12345"
        assert isinstance(result, str)
    
    @pytest.mark.unit
    def test_validate_player_id_with_whitespace(self, domain):
        """Test that player ID with whitespace is stripped."""
        result = domain.validate_player_id("  12345  ")
        assert result == "12345"
    
    @pytest.mark.unit
    def test_validate_player_id_none(self, domain):
        """Test that None player ID raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.validate_player_id(None)
        assert "Player ID is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_player_id_empty_string(self, domain):
        """Test that empty string raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.validate_player_id("")
        assert "Player ID is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_player_id_whitespace_only(self, domain):
        """Test that whitespace-only string raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.validate_player_id("   ")
        assert "Player ID is required" in str(exc_info.value)


class TestSavedPlayersDomainNormalizePosition:
    """Tests for normalize_position method."""
    
    @pytest.fixture
    def domain(self):
        """Create a SavedPlayersDomain instance for testing."""
        return SavedPlayersDomain()
    
    @pytest.mark.unit
    def test_normalize_position_valid(self, domain):
        """Test that valid position is normalized to uppercase."""
        result = domain.normalize_position("pitcher")
        assert result == "PITCHER"
    
    @pytest.mark.unit
    def test_normalize_position_already_uppercase(self, domain):
        """Test that uppercase position remains uppercase."""
        result = domain.normalize_position("PITCHER")
        assert result == "PITCHER"
    
    @pytest.mark.unit
    def test_normalize_position_mixed_case(self, domain):
        """Test that mixed case position is normalized."""
        result = domain.normalize_position("PiTcHeR")
        assert result == "PITCHER"
    
    @pytest.mark.unit
    def test_normalize_position_with_whitespace(self, domain):
        """Test that position with whitespace is stripped and normalized."""
        result = domain.normalize_position("  pitcher  ")
        assert result == "PITCHER"
    
    @pytest.mark.unit
    def test_normalize_position_none(self, domain):
        """Test that None position returns None."""
        result = domain.normalize_position(None)
        assert result is None
    
    @pytest.mark.unit
    def test_normalize_position_empty_string(self, domain):
        """Test that empty string returns None."""
        result = domain.normalize_position("")
        assert result is None
    
    @pytest.mark.unit
    def test_normalize_position_whitespace_only(self, domain):
        """Test that whitespace-only string returns None."""
        result = domain.normalize_position("   ")
        assert result is None
    
    @pytest.mark.unit
    def test_normalize_position_not_string(self, domain):
        """Test that non-string position raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            domain.normalize_position(123)
        assert "Position must be a string" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_normalize_position_abbreviation(self, domain):
        """Test that position abbreviation is normalized."""
        result = domain.normalize_position("p")
        assert result == "P"


class TestSavedPlayersDomainValidatePlayerInfo:
    """Tests for validate_player_info method."""
    
    @pytest.fixture
    def domain(self):
        """Create a SavedPlayersDomain instance for testing."""
        return SavedPlayersDomain()
    
    @pytest.mark.unit
    def test_validate_player_info_valid(self, domain):
        """Test that valid player info is validated and ID is returned."""
        player_info = {
            "id": 12345,
            "position": "pitcher",
            "name": "Test Player"
        }
        result = domain.validate_player_info(player_info)
        
        assert result == "12345"
        assert player_info["position"] == "PITCHER"
    
    @pytest.mark.unit
    def test_validate_player_info_no_position(self, domain):
        """Test that player info without position is handled."""
        player_info = {
            "id": 12345,
            "name": "Test Player"
        }
        result = domain.validate_player_info(player_info)
        
        assert result == "12345"
        assert player_info["position"] is None
    
    @pytest.mark.unit
    def test_validate_player_info_empty_position(self, domain):
        """Test that empty position is normalized to None."""
        player_info = {
            "id": 12345,
            "position": "",
            "name": "Test Player"
        }
        result = domain.validate_player_info(player_info)
        
        assert result == "12345"
        assert player_info["position"] is None
    
    @pytest.mark.unit
    def test_validate_player_info_missing_id(self, domain):
        """Test that missing ID raises InputValidationError."""
        player_info = {
            "position": "pitcher",
            "name": "Test Player"
        }
        with pytest.raises(InputValidationError):
            domain.validate_player_info(player_info)
    
    @pytest.mark.unit
    def test_validate_player_info_modifies_dict(self, domain):
        """Test that validate_player_info modifies the original dict."""
        player_info = {
            "id": 12345,
            "position": "pitcher"
        }
        domain.validate_player_info(player_info)
        
        # Original dict should be modified
        assert player_info["position"] == "PITCHER"
