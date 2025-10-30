"""
Integration tests for health check endpoints.
Tests the actual API endpoints with real FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


class TestHealthEndpoints:
    """Integration tests for health check endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["message"] == "Cybermetrics API"
        assert data["status"] == "running"
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint returns system status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "firebase_connected" in data
        assert data["status"] == "healthy"
        assert isinstance(data["firebase_connected"], bool)
    
    def test_health_check_structure(self, client):
        """Test health check returns expected data structure"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields are present
        expected_fields = ["status", "firebase_connected"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
