"""
Unit tests for authentication routes.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from routes.auth import signup, login, verify_token
from useCaseHelpers.errors import (
    InputValidationError,
    AuthError,
    DatabaseError,
    DependencyUnavailableError,
    ConflictError,
    UseCaseError,
)


class TestSignupRoute:
    """Tests for signup route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signup_success(self):
        """Test successful signup."""
        mock_service = Mock()
        mock_service.signup = AsyncMock(return_value={
            "user_id": "123",
            "email": "test@example.com"
        })
        
        signup_data = Mock()
        
        result = await signup(signup_data, mock_service)
        
        assert result["user_id"] == "123"
        mock_service.signup.assert_called_once_with(signup_data)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signup_input_validation_error(self):
        """Test signup with invalid input."""
        mock_service = Mock()
        mock_service.signup = AsyncMock(side_effect=InputValidationError("Invalid email"))
        
        with pytest.raises(HTTPException) as exc_info:
            await signup(Mock(), mock_service)
        
        assert exc_info.value.status_code == 400
        assert "Invalid email" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signup_conflict_error(self):
        """Test signup with existing user."""
        mock_service = Mock()
        mock_service.signup = AsyncMock(side_effect=ConflictError("User already exists"))
        
        with pytest.raises(HTTPException) as exc_info:
            await signup(Mock(), mock_service)
        
        assert exc_info.value.status_code == 409
        assert "User already exists" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signup_database_error(self):
        """Test signup with database error."""
        mock_service = Mock()
        mock_service.signup = AsyncMock(side_effect=DatabaseError("DB connection failed"))
        
        with pytest.raises(HTTPException) as exc_info:
            await signup(Mock(), mock_service)
        
        assert exc_info.value.status_code == 500
        assert "DB connection failed" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signup_use_case_error(self):
        """Test signup with use case error."""
        mock_service = Mock()
        mock_service.signup = AsyncMock(side_effect=UseCaseError("Business logic error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await signup(Mock(), mock_service)
        
        assert exc_info.value.status_code == 422
        assert "Business logic error" in exc_info.value.detail


class TestLoginRoute:
    """Tests for login route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        mock_service = Mock()
        mock_service.login = AsyncMock(return_value={
            "token": "abc123",
            "user_id": "456"
        })
        
        login_data = Mock()
        
        result = await login(login_data, mock_service)
        
        assert result["token"] == "abc123"
        mock_service.login.assert_called_once_with(login_data)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_input_validation_error(self):
        """Test login with invalid input."""
        mock_service = Mock()
        mock_service.login = AsyncMock(side_effect=InputValidationError("Invalid credentials"))
        
        with pytest.raises(HTTPException) as exc_info:
            await login(Mock(), mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_auth_error(self):
        """Test login with authentication error."""
        mock_service = Mock()
        mock_service.login = AsyncMock(side_effect=AuthError("Invalid password"))
        
        with pytest.raises(HTTPException) as exc_info:
            await login(Mock(), mock_service)
        
        assert exc_info.value.status_code == 401
        assert "Invalid password" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_dependency_unavailable_error(self):
        """Test login with service unavailable."""
        mock_service = Mock()
        mock_service.login = AsyncMock(side_effect=DependencyUnavailableError("Firebase unavailable"))
        
        with pytest.raises(HTTPException) as exc_info:
            await login(Mock(), mock_service)
        
        assert exc_info.value.status_code == 503
        assert "Firebase unavailable" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_database_error(self):
        """Test login with database error."""
        mock_service = Mock()
        mock_service.login = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await login(Mock(), mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_use_case_error(self):
        """Test login with use case error."""
        mock_service = Mock()
        mock_service.login = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await login(Mock(), mock_service)
        
        assert exc_info.value.status_code == 422


class TestVerifyTokenRoute:
    """Tests for verify_token route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_success(self):
        """Test successful token verification."""
        mock_service = Mock()
        mock_service.verify_token = AsyncMock(return_value={"user_id": "123"})
        
        result = await verify_token(mock_service, "Bearer abc123")
        
        assert result["user_id"] == "123"
        mock_service.verify_token.assert_called_once_with("abc123")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_missing_header(self):
        """Test verify_token with missing authorization header."""
        mock_service = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, None)
        
        assert exc_info.value.status_code == 401
        assert "Authorization header missing" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_invalid_format(self):
        """Test verify_token with invalid header format."""
        mock_service = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, "InvalidFormat")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_not_bearer(self):
        """Test verify_token with non-Bearer token."""
        mock_service = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, "Basic abc123")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_auth_error(self):
        """Test verify_token with invalid token."""
        mock_service = Mock()
        mock_service.verify_token = AsyncMock(side_effect=AuthError("Invalid token"))
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, "Bearer abc123")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_use_case_error(self):
        """Test verify_token with use case error."""
        mock_service = Mock()
        mock_service.verify_token = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, "Bearer abc123")
        
        assert exc_info.value.status_code == 422
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_database_error(self):
        """Test verify_token with database error."""
        mock_service = Mock()
        mock_service.verify_token = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_service, "Bearer abc123")
        
        # DatabaseError inherits from UseCaseError, so it's caught by UseCaseError handler
        assert exc_info.value.status_code == 422
