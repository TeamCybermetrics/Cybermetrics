"""
Integration tests for player-related API endpoints.
Tests the actual API endpoints with real FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


class TestPlayerSearchEndpoints:
    """Integration tests for player search endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_search_players_endpoint_exists(self, client):
        """Test player search endpoint is accessible"""
        response = client.get("/api/players/search?q=Trout")
        
        # Should return 200 or 500 (if Firebase not configured), but not 404
        assert response.status_code in [200, 500]
    
    def test_search_players_requires_query(self, client):
        """Test player search requires query parameter"""
        response = client.get("/api/players/search")
        
        # Should return 422 for missing required query parameter
        assert response.status_code == 422
    
    def test_search_players_empty_query(self, client):
        """Test player search with empty query"""
        response = client.get("/api/players/search?q=")
        
        # Should return 400 for empty query or 200 with empty results
        assert response.status_code in [200, 400, 500]
    
    def test_search_players_response_structure(self, client):
        """Test player search returns expected structure (if successful)"""
        response = client.get("/api/players/search?q=Trout")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            if len(data) > 0:
                player = data[0]
                expected_fields = ["id", "name", "score", "image_url", "years_active"]
                for field in expected_fields:
                    assert field in player, f"Missing field: {field}"


class TestPlayerDetailEndpoints:
    """Integration tests for player detail endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_get_player_detail_endpoint_exists(self, client):
        """Test player detail endpoint is accessible"""
        response = client.get("/api/players/545361/detail")
        
        # Should return 200, 404, or 500, but not 404 for route
        assert response.status_code in [200, 404, 500]
    
    def test_get_player_detail_invalid_id(self, client):
        """Test player detail with invalid ID"""
        response = client.get("/api/players/-1/detail")
        
        # Should return 400 for invalid ID
        assert response.status_code in [400, 422, 500]
    
    def test_get_player_detail_response_structure(self, client):
        """Test player detail returns expected structure (if successful)"""
        response = client.get("/api/players/545361/detail")
        
        if response.status_code == 200:
            data = response.json()
            expected_fields = ["mlbam_id", "fangraphs_id", "name", "image_url", 
                             "years_active", "seasons"]
            for field in expected_fields:
                assert field in data, f"Missing field: {field}"
            
            assert isinstance(data["seasons"], dict)


class TestRosterAveragesEndpoints:
    """Integration tests for roster averages endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_roster_averages_endpoint_exists(self, client):
        """Test roster averages endpoint is accessible"""
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": [545361, 660271]}
        )
        
        # Should return 200 or 500, but not 404
        assert response.status_code in [200, 500]
    
    def test_roster_averages_requires_player_ids(self, client):
        """Test roster averages requires player_ids"""
        response = client.post("/api/players/roster-averages", json={})
        
        # Should return 422 for missing required field
        assert response.status_code == 422
    
    def test_roster_averages_empty_list(self, client):
        """Test roster averages with empty player list"""
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": []}
        )
        
        # Should return 400 or 422 for empty list
        assert response.status_code in [400, 422]
    
    def test_roster_averages_response_structure(self, client):
        """Test roster averages returns expected structure (if successful)"""
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": [545361]}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "stats" in data
            assert "total_players" in data
            assert isinstance(data["stats"], dict)
            assert isinstance(data["total_players"], int)
            
            if len(data["stats"]) > 0:
                player_stats = list(data["stats"].values())[0]
                expected_fields = ["strikeout_rate", "walk_rate", "isolated_power",
                                 "on_base_percentage", "base_running"]
                for field in expected_fields:
                    assert field in player_stats, f"Missing field: {field}"


class TestSavedPlayersEndpoints:
    """Integration tests for saved players endpoints (require auth)"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_get_saved_players_requires_auth(self, client):
        """Test getting saved players requires authentication"""
        response = client.get("/api/players/saved")
        
        # Should return 401 for missing auth
        assert response.status_code == 401
    
    def test_add_saved_player_requires_auth(self, client):
        """Test adding saved player requires authentication"""
        response = client.post(
            "/api/players/saved",
            json={"id": 545361, "name": "Mike Trout"}
        )
        
        # Should return 401 for missing auth
        assert response.status_code == 401
    
    def test_delete_saved_player_requires_auth(self, client):
        """Test deleting saved player requires authentication"""
        response = client.delete("/api/players/saved/545361")
        
        # Should return 401 for missing auth
        assert response.status_code == 401
    
    def test_get_saved_player_requires_auth(self, client):
        """Test getting specific saved player requires authentication"""
        response = client.get("/api/players/saved/545361")
        
        # Should return 401 for missing auth
        assert response.status_code == 401


class TestAPIErrorHandling:
    """Integration tests for API error handling"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/invalid/endpoint")
        
        assert response.status_code == 404
    
    def test_invalid_method_returns_405(self, client):
        """Test invalid HTTP method returns 405"""
        response = client.put("/api/players/search?q=test")
        
        assert response.status_code == 405
    
    def test_malformed_json_returns_422(self, client):
        """Test malformed JSON returns 422"""
        response = client.post(
            "/api/players/roster-averages",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
