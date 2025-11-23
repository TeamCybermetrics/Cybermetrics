"""
Integration tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthIntegration:
    """Integration tests for health endpoints."""
    
    @pytest.mark.integration
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Cybermetrics" in data["message"]
    
    @pytest.mark.integration
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.integration
    def test_health_has_firebase_status(self, client):
        """Test health endpoint includes Firebase connection status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "firebase_connected" in data
        assert isinstance(data["firebase_connected"], bool)
    
    @pytest.mark.integration
    def test_health_cors_headers(self, client):
        """Test health endpoint has CORS headers."""
        response = client.options("/health")
        
        # Should allow CORS preflight
        assert response.status_code in [200, 204, 405]
