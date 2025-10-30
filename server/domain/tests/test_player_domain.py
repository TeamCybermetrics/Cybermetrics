import pytest
from fastapi import HTTPException, status
from domain.player_domain import PlayerDomain
from models.players import PlayerSearchResult, PlayerDetail, SeasonStats


class TestPlayerDomain:
    """Unit tests for PlayerDomain business logic"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.player_domain = PlayerDomain()
    
    # Test validate_search_query
    def test_validate_search_query_valid(self):
        """Test validation passes with valid query"""
        query = "Mike Trout"
        # Should not raise any exception
        self.player_domain.validate_search_query(query)
    
    def test_validate_search_query_empty(self):
        """Test validation fails with empty query"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_search_query("")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Search query is required" in str(exc_info.value.detail)
    
    def test_validate_search_query_whitespace(self):
        """Test validation fails with whitespace-only query"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_search_query("   ")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Search query is required" in str(exc_info.value.detail)
    
    def test_validate_search_query_none(self):
        """Test validation fails with None query"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_search_query(None)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Search query is required" in str(exc_info.value.detail)
    
    # Test validate_player_id
    def test_validate_player_id_valid(self):
        """Test validation passes with valid player ID"""
        player_id = 12345
        # Should not raise any exception
        self.player_domain.validate_player_id(player_id)
    
    def test_validate_player_id_zero(self):
        """Test validation fails with zero player ID"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_player_id(0)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid player ID" in str(exc_info.value.detail)
    
    def test_validate_player_id_negative(self):
        """Test validation fails with negative player ID"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_player_id(-1)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid player ID" in str(exc_info.value.detail)
    
    def test_validate_player_id_none(self):
        """Test validation fails with None player ID"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.validate_player_id(None)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid player ID" in str(exc_info.value.detail)
    
    # Test _get_player_image_url
    def test_get_player_image_url(self):
        """Test player image URL generation"""
        player_id = 545361
        expected_url = "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/545361/headshot/67/current"
        assert self.player_domain._get_player_image_url(player_id) == expected_url
    
    # Test _get_years_active
    def test_get_years_active_single_year(self):
        """Test years active with single season"""
        seasons = {"2023": {}}
        assert self.player_domain._get_years_active(seasons) == "2023"
    
    def test_get_years_active_multiple_years(self):
        """Test years active with multiple seasons"""
        seasons = {"2020": {}, "2021": {}, "2023": {}}
        assert self.player_domain._get_years_active(seasons) == "2020-2023"
    
    def test_get_years_active_empty(self):
        """Test years active with no seasons"""
        seasons = {}
        assert self.player_domain._get_years_active(seasons) == "Unknown"
    
    def test_get_years_active_none(self):
        """Test years active with None"""
        assert self.player_domain._get_years_active(None) == "Unknown"
    
    # Test fuzzy_search
    def test_fuzzy_search_with_matches(self):
        """Test fuzzy search returns matching players"""
        players = [
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}},
            {"mlbam_id": 660271, "name": "Shohei Ohtani", "seasons": {"2023": {}}},
            {"mlbam_id": 592450, "name": "Mookie Betts", "seasons": {"2023": {}}}
        ]
        
        results = self.player_domain.fuzzy_search(players, "Mike", limit=5, score_cutoff=60)
        
        assert len(results) > 0
        assert all(isinstance(r, PlayerSearchResult) for r in results)
        assert results[0].name == "Mike Trout"
    
    def test_fuzzy_search_empty_query(self):
        """Test fuzzy search with empty query returns empty list"""
        players = [
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}}
        ]
        
        results = self.player_domain.fuzzy_search(players, "", limit=5)
        assert results == []
    
    def test_fuzzy_search_no_matches(self):
        """Test fuzzy search with no matches returns empty list"""
        players = [
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}}
        ]
        
        results = self.player_domain.fuzzy_search(players, "xyz123", limit=5, score_cutoff=90)
        assert results == []
    
    def test_fuzzy_search_filters_invalid_ids(self):
        """Test fuzzy search filters out invalid player IDs"""
        players = [
            {"mlbam_id": 0, "name": "Invalid Player", "seasons": {"2023": {}}},
            {"mlbam_id": -1, "name": "Another Invalid", "seasons": {"2023": {}}},
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}}
        ]
        
        results = self.player_domain.fuzzy_search(players, "player", limit=5, score_cutoff=50)
        
        # Should only include valid player ID
        assert all(r.id > 0 for r in results)
    
    # Test build_player_detail
    def test_build_player_detail_valid(self):
        """Test building player detail with valid data"""
        player_data = {
            "mlbam_id": 545361,
            "fangraphs_id": "10155",
            "name": "Mike Trout",
            "team_abbrev": "LAA",
            "overall_score": 95.5,
            "seasons": {
                "2023": {
                    "plate_appearances": 600,
                    "strikeout_rate": 0.20,
                    "walk_rate": 0.15,
                    "isolated_power": 0.250,
                    "on_base_percentage": 0.380,
                    "base_running": 2.5
                }
            }
        }
        
        result = self.player_domain.build_player_detail(player_data)
        
        assert isinstance(result, PlayerDetail)
        assert result.mlbam_id == 545361
        assert result.name == "Mike Trout"
        assert result.team_abbrev == "LAA"
        assert result.overall_score == 95.5
        assert "2023" in result.seasons
        assert isinstance(result.seasons["2023"], SeasonStats)
    
    def test_build_player_detail_handles_def_field(self):
        """Test building player detail handles 'def' field (Python keyword)"""
        player_data = {
            "mlbam_id": 545361,
            "fangraphs_id": 10155,
            "name": "Mike Trout",
            "seasons": {
                "2023": {
                    "plate_appearances": 600,
                    "def": 10.5  # Python keyword
                }
            }
        }
        
        result = self.player_domain.build_player_detail(player_data)
        
        # Should rename 'def' to 'def_'
        assert hasattr(result.seasons["2023"], "def_")
    
    def test_build_player_detail_empty_data(self):
        """Test building player detail with empty data raises exception"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.build_player_detail({})
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Player not found" in str(exc_info.value.detail)
    
    def test_build_player_detail_none(self):
        """Test building player detail with None raises exception"""
        with pytest.raises(HTTPException) as exc_info:
            self.player_domain.build_player_detail(None)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Player not found" in str(exc_info.value.detail)
