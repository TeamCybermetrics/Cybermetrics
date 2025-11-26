"""
Integration tests for recommendations endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, Mock, AsyncMock
from dependency.dependencies import get_recommendation_service


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestRecommendationsIntegration:
    """Integration tests for recommendations endpoint."""
    
    @pytest.mark.integration
    def test_recommendations_endpoint_exists(self, client):
        """Test recommendations endpoint is accessible."""
        response = client.post(
            "/api/recommendations",
            json={"player_ids": [660271]}
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_recommendations_missing_payload(self, client):
        """Test recommendations without payload."""
        response = client.post("/api/recommendations")
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_recommendations_empty_player_ids(self, client):
        """Test recommendations with empty player IDs."""
        response = client.post(
            "/api/recommendations",
            json={"player_ids": []}
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.integration
    def test_recommendations_invalid_player_ids(self, client):
        """Test recommendations with invalid player IDs."""
        response = client.post(
            "/api/recommendations",
            json={"player_ids": ["invalid"]}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_recommendations_success_flow(self, client):
        """Test successful recommendations flow."""
        # Mock the service
        mock_service = Mock()
        mock_service.recommend_players = AsyncMock(return_value=[
            {
                "id": 123456,
                "name": "Recommended Player",
                "score": 95.0,
                "image_url": "http://example.com/image.jpg",
                "years_active": "2020-2024"
            }
        ])
        
        # Override the dependency using FastAPI's dependency override
        app.dependency_overrides[get_recommendation_service] = lambda: mock_service
        
        try:
            # Send at least 9 player IDs as it is more logical and a requirement now for the recommendations
            response = client.post(
                "/api/recommendations",
                json={"player_ids": [660271, 545361, 592450, 543037, 543760, 458015, 430945, 425844, 543059]}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        finally:
            # Clean up the override
            app.dependency_overrides.clear()
    
    @pytest.mark.integration
    def test_recommendations_trailing_slash(self, client):
        """Test recommendations endpoint with trailing slash."""
        response = client.post(
            "/api/recommendations/",
            json={"player_ids": [660271]}
        )
        
        # Should work with or without trailing slash
        assert response.status_code != 404
    
    @pytest.mark.integration
    def test_recommendations_returns_json(self, client):
        """Test recommendations returns JSON."""
        response = client.post(
            "/api/recommendations",
            json={"player_ids": [660271]}
        )
        
        assert "application/json" in response.headers["content-type"]
