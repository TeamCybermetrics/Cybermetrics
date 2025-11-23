"""
Unit tests for AuthDomain helper class.
"""
import pytest
from useCaseHelpers.auth_helper import AuthDomain
from useCaseHelpers.errors import InputValidationError, AuthError
from dtos.auth_dtos import LoginRequest, SignupRequest
from entities.auth import User


class TestAuthDomainValidateSignup:
    """Tests for validate_signup_data method."""
    
    @pytest.fixture
    def auth_domain(self):
        """Create an AuthDomain instance for testing."""
        return AuthDomain()
    
    @pytest.mark.unit
    def test_validate_signup_valid_data(self, auth_domain):
        """Test that valid signup data passes validation."""
        signup_data = SignupRequest(
            email="test@example.com",
            password="password123",
            display_name="Test User"
        )
        # Should not raise exception
        auth_domain.validate_signup_data(signup_data)
    
    @pytest.mark.unit
    def test_validate_signup_none_email(self, auth_domain):
        """Test validation with None email (bypassing Pydantic)."""
        # Create a mock object that bypasses Pydantic validation
        from unittest.mock import Mock
        signup_data = Mock()
        signup_data.email = None
        signup_data.password = "password123"
        
        with pytest.raises(InputValidationError) as exc_info:
            auth_domain.validate_signup_data(signup_data)
        assert "Email and password are required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_signup_empty_password(self, auth_domain):
        """Test that empty password raises InputValidationError."""
        from unittest.mock import Mock
        signup_data = Mock()
        signup_data.email = "test@example.com"
        signup_data.password = ""
        
        with pytest.raises(InputValidationError) as exc_info:
            auth_domain.validate_signup_data(signup_data)
        assert "Email and password are required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_signup_short_password(self, auth_domain):
        """Test that password less than 6 characters raises InputValidationError."""
        signup_data = SignupRequest(
            email="test@example.com",
            password="12345",
            display_name="Test User"
        )
        with pytest.raises(InputValidationError) as exc_info:
            auth_domain.validate_signup_data(signup_data)
        assert "Password must be at least 6 characters" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_signup_exactly_six_characters(self, auth_domain):
        """Test that password with exactly 6 characters passes."""
        signup_data = SignupRequest(
            email="test@example.com",
            password="123456",
            display_name="Test User"
        )
        # Should not raise exception
        auth_domain.validate_signup_data(signup_data)


class TestAuthDomainValidateLogin:
    """Tests for validate_login_data method."""
    
    @pytest.fixture
    def auth_domain(self):
        """Create an AuthDomain instance for testing."""
        return AuthDomain()
    
    @pytest.mark.unit
    def test_validate_login_valid_data(self, auth_domain):
        """Test that valid login data passes validation."""
        login_data = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        # Should not raise exception
        auth_domain.validate_login_data(login_data)
    
    @pytest.mark.unit
    def test_validate_login_none_email(self, auth_domain):
        """Test that None email raises InputValidationError."""
        from unittest.mock import Mock
        login_data = Mock()
        login_data.email = None
        login_data.password = "password123"
        
        with pytest.raises(InputValidationError) as exc_info:
            auth_domain.validate_login_data(login_data)
        assert "Email and password are required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_login_empty_password(self, auth_domain):
        """Test that empty password raises InputValidationError."""
        from unittest.mock import Mock
        login_data = Mock()
        login_data.email = "test@example.com"
        login_data.password = ""
        
        with pytest.raises(InputValidationError) as exc_info:
            auth_domain.validate_login_data(login_data)
        assert "Email and password are required" in str(exc_info.value)


class TestAuthDomainValidateToken:
    """Tests for validate_token_format method."""
    
    @pytest.fixture
    def auth_domain(self):
        """Create an AuthDomain instance for testing."""
        return AuthDomain()
    
    @pytest.mark.unit
    def test_validate_token_valid(self, auth_domain):
        """Test that valid token passes validation."""
        token = "valid_token_12345"
        # Should not raise exception
        auth_domain.validate_token_format(token)
    
    @pytest.mark.unit
    def test_validate_token_empty(self, auth_domain):
        """Test that empty token raises AuthError."""
        with pytest.raises(AuthError) as exc_info:
            auth_domain.validate_token_format("")
        assert "Token is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_token_none(self, auth_domain):
        """Test that None token raises AuthError."""
        with pytest.raises(AuthError):
            auth_domain.validate_token_format(None)


class TestAuthDomainValidateUser:
    """Tests for validate_user_exists method."""
    
    @pytest.fixture
    def auth_domain(self):
        """Create an AuthDomain instance for testing."""
        return AuthDomain()
    
    @pytest.mark.unit
    def test_validate_user_exists_valid(self, auth_domain):
        """Test that valid user passes validation."""
        user = User(user_id="123", email="test@example.com", name="Test User")
        # Should not raise exception
        auth_domain.validate_user_exists(user)
    
    @pytest.mark.unit
    def test_validate_user_exists_none(self, auth_domain):
        """Test that None user raises AuthError."""
        with pytest.raises(AuthError) as exc_info:
            auth_domain.validate_user_exists(None)
        assert "Invalid email or password" in str(exc_info.value)
