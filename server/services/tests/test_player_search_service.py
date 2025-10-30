import pytest
from unittest.mock import AsyncMock, Mock
from services.player_search_service import PlayerSearchService
from models.players import PlayerSearchResult, PlayerDetail, SeasonStats


class TestPlayerSearchService:
    """Unit tests for PlayerSearchService"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_player_repository = Mock()
        self.mock_player_domain = Mock()
        self.player_search_service = PlayerSearchService(
            player_repository=self.mock_player_repository,
            player_domain=self.mock_player_domain
        )
    
    # Test search
    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful player search"""
        query = "Mike Trout"
        limit = 5
        score_cutoff = 60
        
        # Mock domain validation
        self.mock_player_domain.validate_search_query.return_value = None
        
        # Mock repository response
        mock_players = [
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}},
            {"mlbam_id": 660271, "name": "Shohei Ohtani", "seasons": {"2023": {}}}
        ]
        self.mock_player_repository.get_all_players = AsyncMock(return_value=mock_players)
        
        # Mock domain fuzzy search
        expected_results = [
            PlayerSearchResult(
                id=545361,
                name="Mike Trout",
                score=95.0,
                image_url="https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/545361/headshot/67/current",
                years_active="2023"
            )
        ]
        self.mock_player_domain.fuzzy_search.return_value = expected_results
        
        result = await self.player_search_service.search(query, limit, score_cutoff)
        
        # Verify domain validation was called
        self.mock_player_domain.validate_search_query.assert_called_once_with(query)
        
        # Verify repository was called
        self.mock_player_repository.get_all_players.assert_called_once()
        
        # Verify domain fuzzy search was called
        self.mock_player_domain.fuzzy_search.assert_called_once_with(
            mock_players, query, limit, score_cutoff
        )
        
        # Verify response
        assert result == expected_results
        assert len(result) == 1
        assert result[0].name == "Mike Trout"
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test search with empty query"""
        query = ""
        
        # Mock domain validation to raise exception
        from fastapi import HTTPException, status
        self.mock_player_domain.validate_search_query.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query is required"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.player_search_service.search(query)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify repository was not called
        self.mock_player_repository.get_all_players.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search with no matching results"""
        query = "NonExistentPlayer"
        
        # Mock domain validation
        self.mock_player_domain.validate_search_query.return_value = None
        
        # Mock repository response
        mock_players = [
            {"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}}
        ]
        self.mock_player_repository.get_all_players = AsyncMock(return_value=mock_players)
        
        # Mock domain fuzzy search returns empty list
        self.mock_player_domain.fuzzy_search.return_value = []
        
        result = await self.player_search_service.search(query)
        
        # Verify response is empty
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_with_custom_parameters(self):
        """Test search with custom limit and score cutoff"""
        query = "Trout"
        limit = 10
        score_cutoff = 80
        
        # Mock domain validation
        self.mock_player_domain.validate_search_query.return_value = None
        
        # Mock repository response
        mock_players = [{"mlbam_id": 545361, "name": "Mike Trout", "seasons": {"2023": {}}}]
        self.mock_player_repository.get_all_players = AsyncMock(return_value=mock_players)
        
        # Mock domain fuzzy search
        self.mock_player_domain.fuzzy_search.return_value = []
        
        await self.player_search_service.search(query, limit, score_cutoff)
        
        # Verify fuzzy search was called with custom parameters
        self.mock_player_domain.fuzzy_search.assert_called_once_with(
            mock_players, query, limit, score_cutoff
        )
    
    # Test get_player_detail
    @pytest.mark.asyncio
    async def test_get_player_detail_success(self):
        """Test successful retrieval of player details"""
        player_id = 545361
        
        # Mock domain validation
        self.mock_player_domain.validate_player_id.return_value = None
        
        # Mock repository response
        mock_player_data = {
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
        self.mock_player_repository.get_player_by_id = AsyncMock(return_value=mock_player_data)
        
        # Mock domain build player detail
        expected_detail = PlayerDetail(
            mlbam_id=545361,
            fangraphs_id="10155",
            name="Mike Trout",
            image_url="https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/545361/headshot/67/current",
            years_active="2023",
            team_abbrev="LAA",
            overall_score=95.5,
            seasons={"2023": SeasonStats(plate_appearances=600, strikeout_rate=0.20)}
        )
        self.mock_player_domain.build_player_detail.return_value = expected_detail
        
        result = await self.player_search_service.get_player_detail(player_id)
        
        # Verify domain validation was called
        self.mock_player_domain.validate_player_id.assert_called_once_with(player_id)
        
        # Verify repository was called
        self.mock_player_repository.get_player_by_id.assert_called_once_with(player_id)
        
        # Verify domain build was called
        self.mock_player_domain.build_player_detail.assert_called_once_with(mock_player_data)
        
        # Verify response
        assert result == expected_detail
        assert result.name == "Mike Trout"
    
    @pytest.mark.asyncio
    async def test_get_player_detail_invalid_id(self):
        """Test get player detail with invalid ID"""
        player_id = -1
        
        # Mock domain validation to raise exception
        from fastapi import HTTPException, status
        self.mock_player_domain.validate_player_id.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player ID"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.player_search_service.get_player_detail(player_id)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify repository was not called
        self.mock_player_repository.get_player_by_id.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_player_detail_not_found(self):
        """Test get player detail when player doesn't exist"""
        player_id = 999999
        
        # Mock domain validation
        self.mock_player_domain.validate_player_id.return_value = None
        
        # Mock repository response
        self.mock_player_repository.get_player_by_id = AsyncMock(return_value=None)
        
        # Mock domain build to raise exception
        from fastapi import HTTPException, status
        self.mock_player_domain.build_player_detail.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.player_search_service.get_player_detail(player_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
