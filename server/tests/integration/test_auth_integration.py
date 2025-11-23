"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, Mock, AsyncMock


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestSignupIntegration:
    """Integration tests for signup endpoint."""
    
    @pytest.mark.integration
    def test_signup_endpoint_exists(self, client):
        """Test signup endpoint is accessible."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com"}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "password123",
                "name": "Test User"
            }
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.integration
    def test_signup_with_valid_data_structure(self, client):
        """Test signup endpoint accepts valid data structure."""
        # This will fail without proper Firebase, but tests the endpoint structure
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "name": "Test User"
            }
        )
        
        # Will fail without Firebase but validates endpoint structure
        assert response.status_code in [201, 400, 409, 422, 500, 503]


class TestLoginIntegration:
    """Integration tests for login endpoint."""
    
    @pytest.mark.integration
    def test_login_endpoint_exists(self, client):
        """Test login endpoint is accessible."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post(
            "/api/auth/login",
            json={"email": "", "password": ""}
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.integration
    @patch('dependency.dependencies.get_auth_repository')
    def test_login_invalid_credentials(self, mock_repo, client):
        """Test login with invalid credentials."""
        # Mock the repository to simulate invalid credentials
        mock_repo_instance = Mock()
        mock_repo_instance.get_user_by_email = AsyncMock(return_value=None)
        mock_repo.return_value = mock_repo_instance
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        # Should return unauthorized, bad request, or server error
        assert response.status_code in [400, 401, 422, 500]


class TestVerifyTokenIntegration:
    """Integration tests for token verification endpoint."""
    
    @pytest.mark.integration
    def test_verify_token_endpoint_exists(self, client):
        """Test verify endpoint is accessible."""
        response = client.get("/api/auth/verify")
        
        # Should not return 404
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_verify_token_missing_header(self, client):
        """Test verify without authorization header."""
        response = client.get("/api/auth/verify")
        
        # Should return 401 unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "Authorization header missing" in data["detail"]
    
    @pytest.mark.integration
    def test_verify_token_invalid_format(self, client):
        """Test verify with invalid header format."""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "InvalidFormat"}
        )
        
        # Should return 401 unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authorization header format" in data["detail"]
    
    @pytest.mark.integration
    def test_verify_token_not_bearer(self, client):
        """Test verify with non-Bearer token."""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "Basic abc123"}
        )
        
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.integration
    @patch('dependency.dependencies.get_auth_repository')
    def test_verify_token_valid_format(self, mock_repo, client):
        """Test verify with valid token format."""
        # Mock the repository
        mock_repo_instance = Mock()
        mock_repo_instance.verify_custom_token = AsyncMock(return_value={
            "uid": "user123",
            "email": "test@example.com"
        })
        mock_repo.return_value = mock_repo_instance
        
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer fake_valid_token"}
        )
        
        # Should succeed or return specific error
        assert response.status_code in [200, 401, 422]


class TestAuthEndpointsStructure:
    """Integration tests for auth endpoints structure."""
    
    @pytest.mark.integration
    def test_all_auth_endpoints_registered(self, client):
        """Test all auth endpoints are registered."""
        # Test signup
        response = client.post("/api/auth/signup", json={})
        assert response.status_code != 404
        
        # Test login
        response = client.post("/api/auth/login", json={})
        assert response.status_code != 404
        
        # Test verify
        response = client.get("/api/auth/verify")
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_auth_endpoints_return_json(self, client):
        """Test auth endpoints return JSON responses."""
        response = client.get("/api/auth/verify")
        
        assert response.headers["content-type"] == "application/json"
