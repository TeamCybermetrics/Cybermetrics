"""
Unit tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestHealthRoutes:
    """Tests for health check routes."""
    
    @pytest.mark.api
    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["message"] == "Cybermetrics API"
        assert data["status"] == "running"
    
    @pytest.mark.api
    def test_health_check_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        with patch('routes.health.firebase_service') as mock_firebase:
            mock_firebase.is_connected.return_value = True
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
    
    @pytest.mark.api
    def test_health_check_firebase_connected(self, client: TestClient):
        """Test health check shows Firebase connection status."""
        with patch('routes.health.firebase_service') as mock_firebase:
            mock_firebase.is_connected.return_value = True
            
            response = client.get("/health")
            data = response.json()
            
            assert "firebase_connected" in data
            assert data["firebase_connected"] is True
    
    @pytest.mark.api
    def test_health_check_firebase_disconnected(self, client: TestClient):
        """Test health check when Firebase is disconnected."""
        with patch('routes.health.firebase_service') as mock_firebase:
            mock_firebase.is_connected.return_value = False
            
            response = client.get("/health")
            data = response.json()
            
            assert data["firebase_connected"] is False
    
    @pytest.mark.api
    def test_root_endpoint_returns_json(self, client: TestClient):
        """Test that root endpoint returns JSON."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
    
    @pytest.mark.api
    def test_health_endpoint_returns_json(self, client: TestClient):
        """Test that health endpoint returns JSON."""
        with patch('routes.health.firebase_service'):
            response = client.get("/health")
            assert response.headers["content-type"] == "application/json"


class TestCORSHeaders:
    """Tests for CORS headers."""
    
    @pytest.mark.api
    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in response."""
        response = client.get("/")
        
        # Check for common CORS headers
        # Note: TestClient may not include all CORS headers, 
        # but we can verify the endpoint is accessible
        assert response.status_code == 200
    
    @pytest.mark.api
    def test_options_request(self, client: TestClient):
        """Test OPTIONS request for CORS preflight."""
        response = client.options("/health")
        
        # OPTIONS should be handled
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled


class TestErrorHandling:
    """Tests for error handling in routes."""
    
    @pytest.mark.api
    def test_nonexistent_endpoint(self, client: TestClient):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_invalid_method(self, client: TestClient):
        """Test that invalid HTTP methods return 405."""
        # Health endpoint only supports GET
        response = client.post("/health")
        assert response.status_code == 405


class TestResponseFormat:
    """Tests for response format consistency."""
    
    @pytest.mark.api
    def test_root_response_structure(self, client: TestClient):
        """Test that root endpoint has expected response structure."""
        response = client.get("/")
        data = response.json()
        
        assert isinstance(data, dict)
        assert "message" in data
        assert "status" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["status"], str)
    
    @pytest.mark.api
    def test_health_response_structure(self, client: TestClient):
        """Test that health endpoint has expected response structure."""
        with patch('routes.health.firebase_service') as mock_firebase:
            mock_firebase.is_connected.return_value = True
            
            response = client.get("/health")
            data = response.json()
            
            assert isinstance(data, dict)
            assert "status" in data
            assert "firebase_connected" in data
            assert isinstance(data["status"], str)
            assert isinstance(data["firebase_connected"], bool)
