"""
Unit tests for PlayerDomain helper class.
"""
import pytest
from useCaseHelpers.player_helper import PlayerDomain
from useCaseHelpers.errors import InputValidationError
from dtos.player_dtos import PlayerSearchResult


class TestPlayerDomainValidation:
    """Tests for PlayerDomain validation methods."""
    
    @pytest.fixture
    def player_domain(self):
        """Create a PlayerDomain instance for testing."""
        return PlayerDomain()
    
    @pytest.mark.unit
    def test_validate_search_query_valid(self, player_domain):
        """Test that valid search queries pass validation."""
        # Should not raise any exception
        player_domain.validate_search_query("Mike Trout")
        player_domain.validate_search_query("Aaron Judge")
        player_domain.validate_search_query("a")  # Single character is valid
    
    @pytest.mark.unit
    def test_validate_search_query_empty_string(self, player_domain):
        """Test that empty string raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            player_domain.validate_search_query("")
        assert "Search query is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_search_query_whitespace_only(self, player_domain):
        """Test that whitespace-only string raises InputValidationError."""
        with pytest.raises(InputValidationError) as exc_info:
            player_domain.validate_search_query("   ")
        assert "Search query is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_search_query_none(self, player_domain):
        """Test that None raises InputValidationError."""
        with pytest.raises(InputValidationError):
            player_domain.validate_search_query(None)


class TestPlayerDomainYearsActive:
    """Tests for _get_years_active method."""
    
    @pytest.fixture
    def player_domain(self):
        """Create a PlayerDomain instance for testing."""
        return PlayerDomain()
    
    @pytest.mark.unit
    def test_get_years_active_single_season(self, player_domain):
        """Test years active for a player with one season."""
        seasons = {"2023": {}}
        result = player_domain._get_years_active(seasons)
        assert result == "2023"
    
    @pytest.mark.unit
    def test_get_years_active_multiple_seasons(self, player_domain):
        """Test years active for a player with multiple seasons."""
        seasons = {"2020": {}, "2021": {}, "2022": {}, "2023": {}}
        result = player_domain._get_years_active(seasons)
        assert result == "2020-2023"
    
    @pytest.mark.unit
    def test_get_years_active_non_consecutive_seasons(self, player_domain):
        """Test years active with non-consecutive seasons."""
        seasons = {"2015": {}, "2018": {}, "2023": {}}
        result = player_domain._get_years_active(seasons)
        assert result == "2015-2023"
    
    @pytest.mark.unit
    def test_get_years_active_empty_dict(self, player_domain):
        """Test years active with empty seasons dict."""
        result = player_domain._get_years_active({})
        assert result == "Unknown"
    
    @pytest.mark.unit
    def test_get_years_active_none(self, player_domain):
        """Test years active with None."""
        result = player_domain._get_years_active(None)
        assert result == "Unknown"
    
    @pytest.mark.unit
    def test_get_years_active_unordered_years(self, player_domain):
        """Test that years are properly sorted."""
        seasons = {"2023": {}, "2020": {}, "2022": {}, "2021": {}}
        result = player_domain._get_years_active(seasons)
        assert result == "2020-2023"


class TestPlayerDomainBuildSearchResult:
    """Tests for building player search results."""
    
    @pytest.fixture
    def player_domain(self):
        """Create a PlayerDomain instance for testing."""
        return PlayerDomain()
    
    @pytest.fixture
    def sample_player(self):
        """Sample player data."""
        return {
            "mlbam_id": 545361,
            "name": "Mike Trout",
            "seasons": {
                "2020": {},
                "2021": {},
                "2022": {},
                "2023": {}
            }
        }
    
    @pytest.mark.unit
    def test_build_player_search_result_valid(self, player_domain, sample_player):
        """Test building a valid player search result."""
        result = player_domain.build_player_search_result(
            sample_player,
            score=95.5
        )
        
        assert result is not None
        assert isinstance(result, PlayerSearchResult)
        assert result.id == 545361
        assert result.name == "Mike Trout"
        assert result.score == 95.5
        assert result.years_active == "2020-2023"
    
    @pytest.mark.unit
    def test_build_player_search_result_with_image_builder(self, player_domain, sample_player):
        """Test building search result with custom image builder."""
        def custom_image_builder(player_id: int) -> str:
            return f"https://example.com/players/{player_id}.jpg"
        
        result = player_domain.build_player_search_result(
            sample_player,
            score=90.0,
            image_builder=custom_image_builder
        )
        
        assert result.image_url == "https://example.com/players/545361.jpg"
    
    @pytest.mark.unit
    def test_build_player_search_result_invalid_mlbam_id(self, player_domain):
        """Test that invalid mlbam_id returns None."""
        invalid_player = {
            "mlbam_id": -1,  # Invalid ID
            "name": "Test Player",
            "seasons": {"2023": {}}
        }
        
        result = player_domain.build_player_search_result(invalid_player, score=80.0)
        assert result is None
    
    @pytest.mark.unit
    def test_build_player_search_result_missing_mlbam_id(self, player_domain):
        """Test that missing mlbam_id returns None."""
        invalid_player = {
            "name": "Test Player",
            "seasons": {"2023": {}}
        }
        
        result = player_domain.build_player_search_result(invalid_player, score=80.0)
        assert result is None
    
    @pytest.mark.unit
    def test_build_player_search_result_zero_mlbam_id(self, player_domain):
        """Test that zero mlbam_id returns None."""
        invalid_player = {
            "mlbam_id": 0,
            "name": "Test Player",
            "seasons": {"2023": {}}
        }
        
        result = player_domain.build_player_search_result(invalid_player, score=80.0)
        assert result is None
    
    @pytest.mark.unit
    def test_build_player_search_result_default_image_url(self, player_domain, sample_player):
        """Test that default image URL is empty string."""
        result = player_domain.build_player_search_result(sample_player, score=85.0)
        assert result.image_url == ""


class TestPlayerDomainFuzzySearch:
    """Tests for fuzzy search functionality."""
    
    @pytest.fixture
    def player_domain(self):
        """Create a PlayerDomain instance for testing."""
        return PlayerDomain()
    
    @pytest.fixture
    def sample_players(self):
        """Sample list of players for testing."""
        return [
            {
                "mlbam_id": 545361,
                "name": "Mike Trout",
                "seasons": {"2020": {}, "2021": {}, "2022": {}, "2023": {}}
            },
            {
                "mlbam_id": 592450,
                "name": "Aaron Judge",
                "seasons": {"2016": {}, "2017": {}, "2023": {}}
            },
            {
                "mlbam_id": 660271,
                "name": "Shohei Ohtani",
                "seasons": {"2018": {}, "2023": {}}
            }
        ]
    
    @pytest.mark.unit
    def test_fuzzy_search_empty_query(self, player_domain, sample_players):
        """Test fuzzy search with empty query returns empty list."""
        results = player_domain.fuzzy_search(sample_players, "")
        assert results == []
    
    @pytest.mark.unit
    def test_fuzzy_search_whitespace_query(self, player_domain, sample_players):
        """Test fuzzy search with whitespace query returns empty list."""
        results = player_domain.fuzzy_search(sample_players, "   ")
        assert results == []
    
    @pytest.mark.unit
    def test_fuzzy_search_exact_match(self, player_domain, sample_players):
        """Test fuzzy search with exact name match."""
        results = player_domain.fuzzy_search(sample_players, "Mike Trout", limit=5)
        
        assert len(results) > 0
        assert results[0].name == "Mike Trout"
        assert results[0].score >= 90  # Exact match should have high score
    
    @pytest.mark.unit
    def test_fuzzy_search_partial_match(self, player_domain, sample_players):
        """Test fuzzy search with partial name match."""
        results = player_domain.fuzzy_search(sample_players, "Trout", limit=5)
        
        assert len(results) > 0
        # Should find Mike Trout
        assert any(r.name == "Mike Trout" for r in results)
    
    @pytest.mark.unit
    def test_fuzzy_search_limit(self, player_domain, sample_players):
        """Test that fuzzy search respects the limit parameter."""
        results = player_domain.fuzzy_search(sample_players, "a", limit=2)
        assert len(results) <= 2
    
    @pytest.mark.unit
    def test_fuzzy_search_score_cutoff(self, player_domain, sample_players):
        """Test that fuzzy search respects score cutoff."""
        results = player_domain.fuzzy_search(
            sample_players,
            "xyz123",  # Query unlikely to match well
            score_cutoff=90
        )
        # All results should have score >= 90 or be empty
        assert all(r.score >= 90 for r in results)
    
    @pytest.mark.unit
    def test_fuzzy_search_empty_player_list(self, player_domain):
        """Test fuzzy search with empty player list."""
        results = player_domain.fuzzy_search([], "Mike Trout")
        assert results == []
    
    @pytest.mark.unit
    def test_fuzzy_search_with_image_builder(self, player_domain, sample_players):
        """Test fuzzy search with custom image builder."""
        def custom_image_builder(player_id: int) -> str:
            return f"https://example.com/{player_id}.png"
        
        results = player_domain.fuzzy_search(
            sample_players,
            "Mike Trout",
            image_builder=custom_image_builder
        )
        
        if results:
            assert "https://example.com/" in results[0].image_url
            assert ".png" in results[0].image_url
