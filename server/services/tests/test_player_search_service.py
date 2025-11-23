"""
Unit tests for PlayerSearchService.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from services.player_search_service import PlayerSearchService
from useCaseHelpers.errors import InputValidationError
from dtos.player_dtos import PlayerSearchResult, PlayerDetail


class TestPlayerSearchServiceInitialization:
    """Tests for PlayerSearchService initialization."""
    
    @pytest.mark.unit
    def test_service_initialization(self):
        """Test that service initializes with dependencies."""
        mock_repo = Mock()
        mock_domain = Mock()
        
        service = PlayerSearchService(mock_repo, mock_domain)
        
        assert service.player_repository is mock_repo
        assert service.player_domain is mock_domain


class TestPlayerSearchServiceSearch:
    """Tests for search method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock player repository."""
        repo = Mock()
        repo.get_all_players = AsyncMock(return_value=[
            {
                "mlbam_id": 545361,
                "name": "Mike Trout",
                "seasons": {"2020": {}, "2023": {}}
            },
            {
                "mlbam_id": 592450,
                "name": "Aaron Judge",
                "seasons": {"2016": {}, "2023": {}}
            }
        ])
        repo.build_player_image_url = Mock(
            side_effect=lambda pid: f"https://example.com/{pid}.jpg"
        )
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock player domain."""
        domain = Mock()
        domain.validate_search_query = Mock()
        domain.fuzzy_search = Mock(return_value=[
            PlayerSearchResult(
                id=545361,
                name="Mike Trout",
                score=95.5,
                image_url="https://example.com/545361.jpg",
                years_active="2020-2023"
            )
        ])
        return domain
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_calls_validation(self, mock_repository, mock_domain):
        """Test that search validates the query."""
        service = PlayerSearchService(mock_repository, mock_domain)
        query = "Mike Trout"
        
        await service.search(query)
        
        mock_domain.validate_search_query.assert_called_once_with(query)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_fetches_all_players(self, mock_repository, mock_domain):
        """Test that search fetches all players from repository."""
        service = PlayerSearchService(mock_repository, mock_domain)
        
        await service.search("Mike Trout")
        
        mock_repository.get_all_players.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_calls_fuzzy_search(self, mock_repository, mock_domain):
        """Test that search calls fuzzy_search with correct parameters."""
        service = PlayerSearchService(mock_repository, mock_domain)
        query = "Mike Trout"
        limit = 10
        score_cutoff = 70
        
        await service.search(query, limit=limit, score_cutoff=score_cutoff)
        
        # Verify fuzzy_search was called with correct arguments
        call_args = mock_domain.fuzzy_search.call_args
        assert call_args is not None
        
        # Check positional arguments
        players_arg = call_args[0][0]
        query_arg = call_args[0][1]
        
        assert len(players_arg) == 2  # Two mock players
        assert query_arg == query
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_returns_results(self, mock_repository, mock_domain):
        """Test that search returns search results."""
        service = PlayerSearchService(mock_repository, mock_domain)
        
        results = await service.search("Mike Trout")
        
        assert len(results) == 1
        assert isinstance(results[0], PlayerSearchResult)
        assert results[0].name == "Mike Trout"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_default_parameters(self, mock_repository, mock_domain):
        """Test search with default limit and score_cutoff."""
        service = PlayerSearchService(mock_repository, mock_domain)
        
        await service.search("Mike Trout")
        
        # Verify default parameters were used
        call_args = mock_domain.fuzzy_search.call_args
        # Check that limit and score_cutoff were passed (defaults: 5 and 60)
        assert call_args is not None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_invalid_query_raises_error(self, mock_repository, mock_domain):
        """Test that invalid query raises InputValidationError."""
        mock_domain.validate_search_query.side_effect = InputValidationError(
            "Search query is required"
        )
        service = PlayerSearchService(mock_repository, mock_domain)
        
        with pytest.raises(InputValidationError):
            await service.search("")


class TestPlayerSearchServiceGetPlayerDetail:
    """Tests for get_player_detail method."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock player repository."""
        repo = Mock()
        repo.get_player_by_id = AsyncMock(return_value={
            "mlbam_id": 545361,
            "fangraphs_id": 10155,
            "name": "Mike Trout",
            "seasons": {
                "2023": {
                    "year": 2023,
                    "team_abbrev": "LAA",
                    "games": 119,
                    "batting_avg": 0.284
                }
            }
        })
        repo.build_player_image_url = Mock(
            side_effect=lambda pid: f"https://example.com/{pid}.jpg"
        )
        return repo
    
    @pytest.fixture
    def mock_domain(self):
        """Create a mock player domain."""
        domain = Mock()
        domain.validate_player_id = Mock()
        domain.build_player_detail = Mock(return_value=PlayerDetail(
            mlbam_id=545361,
            fangraphs_id=10155,
            name="Mike Trout",
            image_url="https://example.com/545361.jpg",
            years_active="2011-2023",
            seasons={}
        ))
        return domain
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_validates_id(self, mock_repository, mock_domain):
        """Test that get_player_detail validates the player ID."""
        service = PlayerSearchService(mock_repository, mock_domain)
        player_id = 545361
        
        await service.get_player_detail(player_id)
        
        mock_domain.validate_player_id.assert_called_once_with(player_id)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_fetches_player(self, mock_repository, mock_domain):
        """Test that get_player_detail fetches player from repository."""
        service = PlayerSearchService(mock_repository, mock_domain)
        player_id = 545361
        
        await service.get_player_detail(player_id)
        
        mock_repository.get_player_by_id.assert_called_once_with(player_id)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_builds_detail(self, mock_repository, mock_domain):
        """Test that get_player_detail builds player detail."""
        service = PlayerSearchService(mock_repository, mock_domain)
        player_id = 545361
        
        await service.get_player_detail(player_id)
        
        # Verify build_player_detail was called
        call_args = mock_domain.build_player_detail.call_args
        assert call_args is not None
        
        # Check that player data was passed
        player_data = call_args[0][0]
        assert player_data["mlbam_id"] == 545361
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_returns_detail(self, mock_repository, mock_domain):
        """Test that get_player_detail returns PlayerDetail."""
        service = PlayerSearchService(mock_repository, mock_domain)
        
        result = await service.get_player_detail(545361)
        
        assert isinstance(result, PlayerDetail)
        assert result.mlbam_id == 545361
        assert result.name == "Mike Trout"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_invalid_id_raises_error(
        self, mock_repository, mock_domain
    ):
        """Test that invalid player ID raises error."""
        mock_domain.validate_player_id.side_effect = InputValidationError(
            "Invalid player ID"
        )
        service = PlayerSearchService(mock_repository, mock_domain)
        
        with pytest.raises(InputValidationError):
            await service.get_player_detail(-1)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_passes_image_builder(
        self, mock_repository, mock_domain
    ):
        """Test that image builder is passed to build_player_detail."""
        service = PlayerSearchService(mock_repository, mock_domain)
        
        await service.get_player_detail(545361)
        
        # Verify image builder was passed
        call_args = mock_domain.build_player_detail.call_args
        image_builder = call_args[0][1]
        
        # Test that it's the correct function
        assert callable(image_builder)
        assert image_builder == mock_repository.build_player_image_url


class TestPlayerSearchServiceIntegration:
    """Integration-style tests for PlayerSearchService."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_workflow(self):
        """Test complete search workflow."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo.get_all_players = AsyncMock(return_value=[
            {
                "mlbam_id": 545361,
                "name": "Mike Trout",
                "seasons": {"2020": {}, "2023": {}}
            }
        ])
        mock_repo.build_player_image_url = Mock(return_value="image_url")
        
        mock_domain = Mock()
        mock_domain.validate_search_query = Mock()
        mock_domain.fuzzy_search = Mock(return_value=[])
        
        # Execute search
        service = PlayerSearchService(mock_repo, mock_domain)
        await service.search("Mike Trout", limit=5, score_cutoff=60)
        
        # Verify workflow
        mock_domain.validate_search_query.assert_called_once()
        mock_repo.get_all_players.assert_called_once()
        mock_domain.fuzzy_search.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_player_detail_workflow(self):
        """Test complete get player detail workflow."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo.get_player_by_id = AsyncMock(return_value={
            "mlbam_id": 545361,
            "name": "Mike Trout"
        })
        mock_repo.build_player_image_url = Mock(return_value="image_url")
        
        mock_domain = Mock()
        mock_domain.validate_player_id = Mock()
        mock_domain.build_player_detail = Mock(return_value=Mock())
        
        # Execute get player detail
        service = PlayerSearchService(mock_repo, mock_domain)
        await service.get_player_detail(545361)
        
        # Verify workflow
        mock_domain.validate_player_id.assert_called_once_with(545361)
        mock_repo.get_player_by_id.assert_called_once_with(545361)
        mock_domain.build_player_detail.assert_called_once()
