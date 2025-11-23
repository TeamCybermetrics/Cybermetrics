"""
Unit tests for DTO (Data Transfer Object) classes.
"""
import pytest
from pydantic import ValidationError
from dtos.player_dtos import PlayerSearchResult, PlayerDetail
from entities.players import SeasonStats


class TestPlayerSearchResult:
    """Tests for PlayerSearchResult DTO."""
    
    @pytest.mark.unit
    def test_player_search_result_valid_creation(self):
        """Test creating a valid PlayerSearchResult."""
        result = PlayerSearchResult(
            id=545361,
            name="Mike Trout",
            score=95.5,
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023"
        )
        
        assert result.id == 545361
        assert result.name == "Mike Trout"
        assert result.score == 95.5
        assert result.image_url == "https://example.com/trout.jpg"
        assert result.years_active == "2011-2023"
    
    @pytest.mark.unit
    def test_player_search_result_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PlayerSearchResult(
                id=545361,
                name="Mike Trout",
                # Missing score, image_url, years_active
            )
    
    @pytest.mark.unit
    def test_player_search_result_invalid_type(self):
        """Test that invalid field types raise ValidationError."""
        with pytest.raises(ValidationError):
            PlayerSearchResult(
                id="not_an_int",  # Should be int
                name="Mike Trout",
                score=95.5,
                image_url="https://example.com/trout.jpg",
                years_active="2011-2023"
            )
    
    @pytest.mark.unit
    def test_player_search_result_to_dict(self):
        """Test converting PlayerSearchResult to dictionary."""
        result = PlayerSearchResult(
            id=545361,
            name="Mike Trout",
            score=95.5,
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023"
        )
        
        result_dict = result.model_dump()
        assert isinstance(result_dict, dict)
        assert result_dict["id"] == 545361
        assert result_dict["name"] == "Mike Trout"
    
    @pytest.mark.unit
    def test_player_search_result_empty_strings(self):
        """Test PlayerSearchResult with empty strings."""
        result = PlayerSearchResult(
            id=1,
            name="",
            score=0.0,
            image_url="",
            years_active=""
        )
        
        assert result.name == ""
        assert result.image_url == ""
        assert result.years_active == ""


class TestPlayerDetail:
    """Tests for PlayerDetail DTO."""
    
    @pytest.fixture
    def sample_season_stats(self):
        """Sample season stats for testing."""
        return {
            "2023": SeasonStats(
                year=2023,
                team_abbrev="LAA",
                games=119,
                plate_appearances=496,
                at_bats=436,
                runs=67,
                hits=124,
                doubles=18,
                triples=2,
                home_runs=26,
                rbi=72,
                stolen_bases=14,
                caught_stealing=3,
                walks=48,
                strikeouts=103,
                batting_avg=0.284,
                on_base_pct=0.369,
                slugging_pct=0.508,
                ops=0.877,
                ops_plus=147,
                total_bases=221,
                gdp=12,
                hbp=8,
                sac_bunts=0,
                sac_flies=4,
                ibb=5,
                war=5.2
            )
        }
    
    @pytest.mark.unit
    def test_player_detail_valid_creation(self, sample_season_stats):
        """Test creating a valid PlayerDetail."""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023",
            team_abbrev="LAA",
            overall_score=95.5,
            seasons=sample_season_stats
        )
        
        assert detail.mlbam_id == 545361
        assert detail.fangraphs_id == 10155
        assert detail.name == "Mike Trout"
        assert detail.team_abbrev == "LAA"
        assert detail.overall_score == 95.5
        assert "2023" in detail.seasons
    
    @pytest.mark.unit
    def test_player_detail_optional_fields(self, sample_season_stats):
        """Test PlayerDetail with optional fields omitted."""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023",
            seasons=sample_season_stats
        )
        
        assert detail.team_abbrev is None
        assert detail.overall_score == 0.0  # Default value
    
    @pytest.mark.unit
    def test_player_detail_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PlayerDetail(
                mlbam_id=545361,
                name="Mike Trout",
                # Missing fangraphs_id, image_url, years_active, seasons
            )
    
    @pytest.mark.unit
    def test_player_detail_empty_seasons(self):
        """Test PlayerDetail with empty seasons dict."""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023",
            seasons={}
        )
        
        assert detail.seasons == {}
        assert len(detail.seasons) == 0
    
    @pytest.mark.unit
    def test_player_detail_multiple_seasons(self):
        """Test PlayerDetail with multiple seasons."""
        seasons = {
            "2022": SeasonStats(
                year=2022,
                team_abbrev="LAA",
                games=119,
                plate_appearances=496,
                at_bats=436,
                runs=67,
                hits=124,
                doubles=18,
                triples=2,
                home_runs=26,
                rbi=72,
                stolen_bases=14,
                caught_stealing=3,
                walks=48,
                strikeouts=103,
                batting_avg=0.284,
                on_base_pct=0.369,
                slugging_pct=0.508,
                ops=0.877,
                ops_plus=147,
                total_bases=221,
                gdp=12,
                hbp=8,
                sac_bunts=0,
                sac_flies=4,
                ibb=5,
                war=5.2
            ),
            "2023": SeasonStats(
                year=2023,
                team_abbrev="LAA",
                games=82,
                plate_appearances=350,
                at_bats=310,
                runs=45,
                hits=85,
                doubles=15,
                triples=1,
                home_runs=18,
                rbi=44,
                stolen_bases=8,
                caught_stealing=2,
                walks=35,
                strikeouts=75,
                batting_avg=0.274,
                on_base_pct=0.360,
                slugging_pct=0.490,
                ops=0.850,
                ops_plus=140,
                total_bases=152,
                gdp=8,
                hbp=5,
                sac_bunts=0,
                sac_flies=2,
                ibb=3,
                war=3.8
            )
        }
        
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023",
            seasons=seasons
        )
        
        assert len(detail.seasons) == 2
        assert "2022" in detail.seasons
        assert "2023" in detail.seasons
    
    @pytest.mark.unit
    def test_player_detail_to_dict(self, sample_season_stats):
        """Test converting PlayerDetail to dictionary."""
        detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/trout.jpg",
            years_active="2011-2023",
            seasons=sample_season_stats
        )
        
        detail_dict = detail.model_dump()
        assert isinstance(detail_dict, dict)
        assert detail_dict["mlbam_id"] == 545361
        assert detail_dict["name"] == "Mike Trout"
        assert "seasons" in detail_dict
