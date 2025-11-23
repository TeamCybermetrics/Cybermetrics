"""
Unit tests for auth middleware.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from middleware.auth import get_current_user


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create a mock auth service."""
        service = Mock()
        service.verify_token = AsyncMock(return_value={"user_id": "user123"})
        return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_auth_service):
        """Test get_current_user with valid Bearer token."""
        authorization = "Bearer valid_token_12345"
        
        result = await get_current_user(mock_auth_service, authorization)
        
        assert result == "user123"
        mock_auth_service.verify_token.assert_called_once_with("valid_token_12345")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_no_authorization(self, mock_auth_service):
        """Test get_current_user with missing authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_auth_service, None)
        
        assert exc_info.value.status_code == 401
        assert "missing" in exc_info.value.detail.lower()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_empty_authorization(self, mock_auth_service):
        """Test get_current_user with empty authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_auth_service, "")
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_format_no_bearer(self, mock_auth_service):
        """Test get_current_user with token but no 'Bearer' prefix."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_auth_service, "token12345")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_format_wrong_prefix(self, mock_auth_service):
        """Test get_current_user with wrong prefix."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_auth_service, "Basic token12345")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_format_too_many_parts(self, mock_auth_service):
        """Test get_current_user with too many parts."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_auth_service, "Bearer token extra_part")
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_case_insensitive_bearer(self, mock_auth_service):
        """Test that 'bearer' is case insensitive."""
        authorization = "bearer valid_token_12345"
        
        result = await get_current_user(mock_auth_service, authorization)
        
        assert result == "user123"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_uppercase_bearer(self, mock_auth_service):
        """Test with uppercase BEARER."""
        authorization = "BEARER valid_token_12345"
        
        result = await get_current_user(mock_auth_service, authorization)
        
        assert result == "user123"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_verify_token_called(self, mock_auth_service):
        """Test that verify_token is called with correct token."""
        authorization = "Bearer my_secret_token"
        
        await get_current_user(mock_auth_service, authorization)
        
        mock_auth_service.verify_token.assert_called_once_with("my_secret_token")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_returns_user_id(self, mock_auth_service):
        """Test that only user_id is returned, not full user info."""
        mock_auth_service.verify_token = AsyncMock(return_value={
            "user_id": "user456",
            "email": "test@example.com",
            "name": "Test User"
        })
        
        result = await get_current_user(mock_auth_service, "Bearer token")
        
        assert result == "user456"
        assert isinstance(result, str)
