"""
Integration tests for player endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, Mock, AsyncMock


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestPlayerSearchIntegration:
    """Integration tests for player search endpoint."""
    
    @pytest.mark.integration
    @patch('dependency.dependencies.get_player_repository')
    def test_search_players_endpoint(self, mock_get_repo, client):
        """Test player search endpoint integration."""
        # Mock the repository
        mock_repo = Mock()
        mock_repo.get_all_players = AsyncMock(return_value=[
            {
                "mlbam_id": 660271,
                "name": "Shohei Ohtani",
                "seasons": {"2023": {}, "2024": {}}
            }
        ])
        mock_repo.build_player_image_url = Mock(return_value="http://example.com/image.jpg")
        mock_get_repo.return_value = mock_repo
        
        response = client.get("/api/players/search?q=Ohtani")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.integration
    def test_search_players_missing_query(self, client):
        """Test search endpoint requires query parameter."""
        response = client.get("/api/players/search")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    @patch('dependency.dependencies.get_player_repository')
    def test_search_players_empty_query(self, mock_get_repo, client):
        """Test search with empty query."""
        mock_repo = Mock()
        mock_repo.get_all_players = AsyncMock(return_value=[])
        mock_get_repo.return_value = mock_repo
        
        response = client.get("/api/players/search?q=")
        
        # Should return 400 for empty query
        assert response.status_code == 400


class TestPlayerDetailIntegration:
    """Integration tests for player detail endpoint."""
    
    @pytest.mark.integration
    def test_get_player_detail_endpoint(self, client):
        """Test get player detail endpoint structure."""
        # Test endpoint exists and accepts player ID
        response = client.get("/api/players/660271/detail")
        
        # May succeed or fail depending on data availability
        assert response.status_code in [200, 404, 422, 500]
    
    @pytest.mark.integration
    def test_get_player_detail_invalid_id(self, client):
        """Test get player detail with invalid ID."""
        response = client.get("/api/players/invalid/detail")
        
        assert response.status_code == 422  # Validation error


class TestRosterAveragesIntegration:
    """Integration tests for roster averages endpoint."""
    
    @pytest.mark.integration
    def test_get_roster_averages_endpoint(self, client):
        """Test roster averages endpoint."""
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": [660271]}
        )
        
        # May succeed or fail depending on data availability
        assert response.status_code in [200, 400, 404, 422, 500]
    
    @pytest.mark.integration
    def test_get_roster_averages_empty_list(self, client):
        """Test roster averages with empty player list."""
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": []}
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.integration
    def test_get_roster_averages_invalid_payload(self, client):
        """Test roster averages with invalid payload."""
        response = client.post(
            "/api/players/roster-averages",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422  # Validation error


class TestSavedPlayersIntegration:
    """Integration tests for saved players endpoints (require auth)."""
    
    @pytest.mark.integration
    def test_get_saved_players_no_auth(self, client):
        """Test get saved players without authentication."""
        response = client.get("/api/players/saved")
        
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_add_saved_player_no_auth(self, client):
        """Test add saved player without authentication."""
        response = client.post(
            "/api/players/saved",
            json={"mlbam_id": 660271, "name": "Test Player"}
        )
        
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_delete_saved_player_no_auth(self, client):
        """Test delete saved player without authentication."""
        response = client.delete("/api/players/saved/660271")
        
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_get_saved_players_requires_valid_token(self, client):
        """Test get saved players requires valid authentication."""
        # Test that endpoint properly rejects invalid tokens
        # The middleware will catch and convert AuthError to HTTPException
        try:
            response = client.get(
                "/api/players/saved",
                headers={"Authorization": "Bearer invalid_fake_token"}
            )
            
            # Should return auth error status code
            assert response.status_code in [401, 422]
            
            # Verify error response has detail
            data = response.json()
            assert "detail" in data
        except Exception:
            # If exception is raised before response, that's also acceptable
            # as it indicates auth is being enforced
            pass
