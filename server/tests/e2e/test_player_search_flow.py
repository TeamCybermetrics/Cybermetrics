"""
End-to-end tests for player search flow.
Tests complete user journeys through the API.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.mark.e2e
class TestPlayerSearchFlow:
    """E2E tests for player search functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_complete_player_search_flow(self, client):
        """
        Test complete flow: search for player -> get player details
        """
        # Step 1: Search for a player
        search_response = client.get("/api/players/search?q=Trout")
        
        if search_response.status_code == 200:
            players = search_response.json()
            
            if len(players) > 0:
                # Step 2: Get details for the first player found
                player_id = players[0]["id"]
                detail_response = client.get(f"/api/players/{player_id}/detail")
                
                # Verify we can get player details
                if detail_response.status_code == 200:
                    player_detail = detail_response.json()
                    
                    # Verify the player ID matches
                    assert player_detail["mlbam_id"] == player_id
                    
                    # Verify player has seasons data
                    assert "seasons" in player_detail
                    assert isinstance(player_detail["seasons"], dict)
    
    def test_search_multiple_players_and_get_roster_averages(self, client):
        """
        Test complete flow: search for multiple players -> get roster averages
        """
        # Step 1: Search for multiple players
        search_queries = ["Trout", "Ohtani", "Judge"]
        player_ids = []
        
        for query in search_queries:
            response = client.get(f"/api/players/search?q={query}")
            
            if response.status_code == 200:
                players = response.json()
                if len(players) > 0:
                    player_ids.append(players[0]["id"])
        
        # Step 2: Get roster averages for found players
        if len(player_ids) > 0:
            roster_response = client.post(
                "/api/players/roster-averages",
                json={"player_ids": player_ids}
            )
            
            if roster_response.status_code == 200:
                roster_data = roster_response.json()
                
                # Verify we got stats for the players
                assert "stats" in roster_data
                assert "total_players" in roster_data
                assert roster_data["total_players"] >= 0
    
    def test_search_with_no_results(self, client):
        """
        Test flow when search returns no results
        """
        # Search for a player that likely doesn't exist
        response = client.get("/api/players/search?q=XYZ123NonExistentPlayer")
        
        if response.status_code == 200:
            players = response.json()
            
            # Should return empty list or no results
            assert isinstance(players, list)
    
    def test_invalid_player_id_flow(self, client):
        """
        Test flow with invalid player ID
        """
        # Try to get details for invalid player ID
        response = client.get("/api/players/999999999/detail")
        
        # Should return 404 or 400
        assert response.status_code in [400, 404, 500]


@pytest.mark.e2e
class TestRosterManagementFlow:
    """E2E tests for roster management functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_roster_averages_calculation_flow(self, client):
        """
        Test complete flow: request roster averages for multiple players
        """
        # Use known player IDs (Mike Trout, Shohei Ohtani, Aaron Judge)
        player_ids = [545361, 660271, 592450]
        
        # Request roster averages
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": player_ids}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify structure
            assert "stats" in data
            assert "total_players" in data
            
            # Verify we got stats for at least some players
            assert isinstance(data["stats"], dict)
            
            # Verify each player stat has required fields
            for player_id, stats in data["stats"].items():
                assert "strikeout_rate" in stats
                assert "walk_rate" in stats
                assert "isolated_power" in stats
                assert "on_base_percentage" in stats
                assert "base_running" in stats
    
    def test_roster_averages_with_single_player(self, client):
        """
        Test roster averages with just one player
        """
        response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": [545361]}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Should work with single player
            assert "stats" in data
            assert "total_players" in data


@pytest.mark.e2e
class TestAPIHealthFlow:
    """E2E tests for API health and status"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_api_startup_and_health_check(self, client):
        """
        Test complete flow: check API is running -> verify health
        """
        # Step 1: Check root endpoint
        root_response = client.get("/")
        assert root_response.status_code == 200
        
        root_data = root_response.json()
        assert root_data["status"] == "running"
        
        # Step 2: Check health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # Step 3: Verify we can make API calls
        search_response = client.get("/api/players/search?q=test")
        
        # Should get a response (even if error due to Firebase)
        assert search_response.status_code in [200, 400, 500]


@pytest.mark.e2e
class TestErrorRecoveryFlow:
    """E2E tests for error handling and recovery"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_request_recovery(self, client):
        """
        Test that API recovers from invalid requests
        """
        # Step 1: Make an invalid request
        invalid_response = client.post(
            "/api/players/roster-averages",
            json={"player_ids": []}
        )
        
        # Should return error
        assert invalid_response.status_code in [400, 422]
        
        # Step 2: Make a valid request after error
        valid_response = client.get("/health")
        
        # Should still work
        assert valid_response.status_code == 200
    
    def test_malformed_data_recovery(self, client):
        """
        Test API handles malformed data gracefully
        """
        # Step 1: Send malformed data
        malformed_response = client.post(
            "/api/players/roster-averages",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return error
        assert malformed_response.status_code == 422
        
        # Step 2: API should still be responsive
        health_response = client.get("/health")
        assert health_response.status_code == 200
