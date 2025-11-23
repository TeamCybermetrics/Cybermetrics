"""
Unit tests for AuthRepositoryFirebase with mocked Firebase.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import HTTPException
from firebase_admin import auth as firebase_auth
from infrastructure.auth_repository import AuthRepositoryFirebase, _redact_email
from dtos.auth_dtos import SignupRequest, LoginRequest
from entities.auth import User


class TestRedactEmail:
    """Tests for _redact_email helper function."""
    
    @pytest.mark.unit
    def test_redact_email_valid(self):
        """Test email redaction with valid email."""
        result = _redact_email("test@example.com")
        
        assert result.startswith("<redacted:")
        assert len(result) > 10
    
    @pytest.mark.unit
    def test_redact_email_empty(self):
        """Test email redaction with empty string."""
        result = _redact_email("")
        
        assert result == "<empty>"
    
    @pytest.mark.unit
    def test_redact_email_none(self):
        """Test email redaction with None."""
        result = _redact_email(None)
        
        assert result == "<empty>"


class TestAuthRepositoryInitialization:
    """Tests for AuthRepositoryFirebase initialization."""
    
    @pytest.mark.unit
    def test_repository_initialization(self):
        """Test that repository initializes with database."""
        mock_db = Mock()
        repo = AuthRepositoryFirebase(mock_db)
        
        assert repo.db is mock_db


class TestAuthRepositoryCreateUser:
    """Tests for create_user method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_no_db(self):
        """Test create_user raises error when database is None."""
        repo = AuthRepositoryFirebase(None)
        signup_data = SignupRequest(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.create_user(signup_data)
        
        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_user_success(self, mock_run_in_threadpool, mock_auth):
        """Test successful user creation."""
        mock_db = Mock()
        mock_user = Mock()
        mock_user.uid = "user123"
        mock_user.email = "test@example.com"
        
        # Mock auth.create_user
        async def mock_create_user(*args, **kwargs):
            return mock_user
        
        mock_run_in_threadpool.side_effect = [
            mock_user,  # First call for create_user
            None  # Second call for set
        ]
        
        repo = AuthRepositoryFirebase(mock_db)
        signup_data = SignupRequest(
            email="test@example.com",
            password="password123",
            display_name="Test User"
        )
        
        result = await repo.create_user(signup_data)
        
        assert result["user_id"] == "user123"
        assert result["email"] == "test@example.com"
        assert "successfully" in result["message"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_user_email_exists(self, mock_run_in_threadpool, mock_auth):
        """Test create_user when email already exists."""
        mock_db = Mock()
        
        # Mock the EmailAlreadyExistsError exception class
        mock_auth.EmailAlreadyExistsError = type('EmailAlreadyExistsError', (Exception,), {})
        mock_run_in_threadpool.side_effect = mock_auth.EmailAlreadyExistsError("Email exists")
        
        repo = AuthRepositoryFirebase(mock_db)
        signup_data = SignupRequest(
            email="existing@example.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.create_user(signup_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()


class TestAuthRepositoryGetUserByEmail:
    """Tests for get_user_by_email method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_email_success(self, mock_run_in_threadpool, mock_auth):
        """Test successful user retrieval by email."""
        mock_user = Mock()
        mock_user.uid = "user123"
        mock_user.email = "test@example.com"
        mock_user.display_name = "Test User"
        
        mock_run_in_threadpool.return_value = mock_user
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_email("test@example.com")
        
        assert isinstance(result, User)
        assert result.user_id == "user123"
        assert result.email == "test@example.com"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_email_not_found(self, mock_run_in_threadpool, mock_auth):
        """Test get_user_by_email when user not found."""
        # Mock the UserNotFoundError exception class
        mock_auth.UserNotFoundError = type('UserNotFoundError', (Exception,), {})
        mock_run_in_threadpool.side_effect = mock_auth.UserNotFoundError("Not found")
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_email("nonexistent@example.com")
        
        assert result is None


class TestAuthRepositoryGetUserById:
    """Tests for get_user_by_id method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_id_success(self, mock_run_in_threadpool, mock_auth):
        """Test successful user retrieval by ID."""
        mock_user = Mock()
        mock_user.uid = "user123"
        mock_user.email = "test@example.com"
        mock_user.display_name = "Test User"
        
        mock_run_in_threadpool.return_value = mock_user
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_id("user123")
        
        assert isinstance(result, User)
        assert result.user_id == "user123"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_id_not_found(self, mock_run_in_threadpool, mock_auth):
        """Test get_user_by_id when user not found."""
        # Mock the UserNotFoundError exception class
        mock_auth.UserNotFoundError = type('UserNotFoundError', (Exception,), {})
        mock_run_in_threadpool.side_effect = mock_auth.UserNotFoundError("Not found")
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_id("nonexistent")
        
        assert result is None


class TestAuthRepositoryCreateCustomToken:
    """Tests for create_custom_token method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_custom_token_success(self, mock_run_in_threadpool, mock_auth):
        """Test successful custom token creation."""
        mock_run_in_threadpool.return_value = b"custom_token_bytes"
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.create_custom_token("user123")
        
        assert result == "custom_token_bytes"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_custom_token_failure(self, mock_run_in_threadpool, mock_auth):
        """Test custom token creation failure."""
        mock_run_in_threadpool.side_effect = Exception("Token creation failed")
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.create_custom_token("user123")
        
        assert exc_info.value.status_code == 500


class TestAuthRepositoryVerifyPassword:
    """Tests for verify_password method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.settings')
    async def test_verify_password_no_api_key(self, mock_settings):
        """Test verify_password when API key is not configured."""
        mock_settings.FIREBASE_WEB_API_KEY = ""
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_password("test@example.com", "password")
        
        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.settings')
    @patch('infrastructure.auth_repository.httpx.AsyncClient')
    async def test_verify_password_success(self, mock_client_class, mock_settings):
        """Test successful password verification."""
        mock_settings.FIREBASE_WEB_API_KEY = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"localId": "user123"}
        
        mock_client = Mock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.verify_password("test@example.com", "password123")
        
        assert result == "user123"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.settings')
    @patch('infrastructure.auth_repository.httpx.AsyncClient')
    async def test_verify_password_invalid_credentials(self, mock_client_class, mock_settings):
        """Test password verification with invalid credentials."""
        mock_settings.FIREBASE_WEB_API_KEY = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 400
        
        mock_client = Mock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_password("test@example.com", "wrong_password")
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail


class TestAuthRepositoryVerifyCustomToken:
    """Tests for verify_custom_token method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.jwt')
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_verify_custom_token_success(self, mock_run_in_threadpool, mock_auth, mock_jwt):
        """Test successful token verification."""
        mock_jwt.decode.return_value = {"uid": "user123"}
        
        mock_user = Mock()
        mock_user.uid = "user123"
        mock_user.email = "test@example.com"
        mock_run_in_threadpool.return_value = mock_user
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.verify_custom_token("test_token")
        
        assert result["user_id"] == "user123"
        assert result["email"] == "test@example.com"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.jwt')
    async def test_verify_custom_token_no_uid(self, mock_jwt):
        """Test token verification with no uid in token."""
        mock_jwt.decode.return_value = {}
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_custom_token("test_token")
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.jwt')
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_verify_custom_token_user_not_found(self, mock_run_in_threadpool, mock_auth, mock_jwt):
        """Test token verification when user not found."""
        mock_jwt.decode.return_value = {"uid": "user123"}
        mock_auth.UserNotFoundError = type('UserNotFoundError', (Exception,), {})
        mock_run_in_threadpool.side_effect = mock_auth.UserNotFoundError("Not found")
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_custom_token("test_token")
        
        assert exc_info.value.status_code == 401


class TestAuthRepositoryStoreUserData:
    """Tests for store_user_data method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_user_data_success(self):
        """Test successful user data storage."""
        mock_db = Mock()
        mock_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_ref
        
        repo = AuthRepositoryFirebase(mock_db)
        user_data = {"name": "Test User", "age": 30}
        
        result = await repo.store_user_data("user123", user_data)
        
        assert result is True
        mock_ref.set.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_user_data_error(self):
        """Test store_user_data handles errors."""
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.set.side_effect = Exception("DB error")
        
        repo = AuthRepositoryFirebase(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.store_user_data("user123", {})
        
        assert exc_info.value.status_code == 500


class TestAuthRepositoryCreateIdToken:
    """Tests for create_id_token method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_id_token_success(self, mock_run_in_threadpool, mock_auth):
        """Test successful ID token creation."""
        mock_run_in_threadpool.return_value = b"id_token_bytes"
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.create_id_token("user123")
        
        assert result == "id_token_bytes"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_id_token_failure(self, mock_run_in_threadpool, mock_auth):
        """Test ID token creation failure."""
        mock_run_in_threadpool.side_effect = Exception("Token creation failed")
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.create_id_token("user123")
        
        assert exc_info.value.status_code == 500


class TestAuthRepositoryVerifyPasswordEdgeCases:
    """Tests for verify_password edge cases."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.settings')
    @patch('infrastructure.auth_repository.httpx.AsyncClient')
    async def test_verify_password_no_uid_in_response(self, mock_client_class, mock_settings):
        """Test password verification when response has no uid."""
        mock_settings.FIREBASE_WEB_API_KEY = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No localId
        
        mock_client = Mock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_password("test@example.com", "password")
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.settings')
    @patch('infrastructure.auth_repository.httpx.AsyncClient')
    async def test_verify_password_network_error(self, mock_client_class, mock_settings):
        """Test password verification with network error."""
        mock_settings.FIREBASE_WEB_API_KEY = "test_api_key"
        
        mock_client = Mock()
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        repo = AuthRepositoryFirebase(Mock())
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.verify_password("test@example.com", "password")
        
        assert exc_info.value.status_code == 500


class TestAuthRepositoryCreateUserGeneralException:
    """Tests for create_user general exception handling."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_create_user_general_exception(self, mock_run_in_threadpool, mock_auth):
        """Test create_user handles general exceptions."""
        mock_db = Mock()
        
        # Mock EmailAlreadyExistsError as a proper exception
        mock_auth.EmailAlreadyExistsError = type('EmailAlreadyExistsError', (Exception,), {})
        
        # Raise a different exception (not EmailAlreadyExistsError)
        mock_run_in_threadpool.side_effect = RuntimeError("Unexpected error")
        
        repo = AuthRepositoryFirebase(mock_db)
        signup_data = SignupRequest(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await repo.create_user(signup_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to create user" in exc_info.value.detail


class TestAuthRepositoryGetUserGeneralExceptions:
    """Tests for get_user methods general exception handling."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_email_general_exception(self, mock_run_in_threadpool, mock_auth):
        """Test get_user_by_email handles general exceptions."""
        # Mock UserNotFoundError as a proper exception
        mock_auth.UserNotFoundError = type('UserNotFoundError', (Exception,), {})
        
        # Raise a different exception (not UserNotFoundError)
        mock_run_in_threadpool.side_effect = RuntimeError("Unexpected error")
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_email("test@example.com")
        
        assert result is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('infrastructure.auth_repository.auth')
    @patch('infrastructure.auth_repository.run_in_threadpool')
    async def test_get_user_by_id_general_exception(self, mock_run_in_threadpool, mock_auth):
        """Test get_user_by_id handles general exceptions."""
        # Mock UserNotFoundError as a proper exception
        mock_auth.UserNotFoundError = type('UserNotFoundError', (Exception,), {})
        
        # Raise a different exception (not UserNotFoundError)
        mock_run_in_threadpool.side_effect = RuntimeError("Unexpected error")
        
        repo = AuthRepositoryFirebase(Mock())
        result = await repo.get_user_by_id("user123")
        
        assert result is None
