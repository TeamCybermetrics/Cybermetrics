"""
Unit tests for recommendations routes.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from routes.recommendations import recommend_players
from useCaseHelpers.errors import InputValidationError, QueryError, UseCaseError


class TestRecommendationsRoute:
    """Tests for recommendations route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_players_success(self):
        """Test successful player recommendations."""
        mock_service = Mock()
        mock_service.recommend_players = AsyncMock(return_value=[
            {"id": 1, "name": "Player 1", "score": 95.0}
        ])
        
        request = Mock()
        request.player_ids = [12345, 67890]
        
        result = await recommend_players(request, mock_service)
        
        assert len(result) == 1
        mock_service.recommend_players.assert_called_once_with([12345, 67890])
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_players_input_validation_error(self):
        """Test InputValidationError handling."""
        mock_service = Mock()
        mock_service.recommend_players = AsyncMock(
            side_effect=InputValidationError("Invalid player IDs")
        )
        
        request = Mock()
        request.player_ids = []
        
        with pytest.raises(HTTPException) as exc_info:
            await recommend_players(request, mock_service)
        
        assert exc_info.value.status_code == 400
        assert "Invalid player IDs" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_players_query_error(self):
        """Test QueryError handling."""
        mock_service = Mock()
        mock_service.recommend_players = AsyncMock(
            side_effect=QueryError("Players not found")
        )
        
        request = Mock()
        request.player_ids = [99999]
        
        with pytest.raises(HTTPException) as exc_info:
            await recommend_players(request, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Players not found" in exc_info.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommend_players_use_case_error(self):
        """Test UseCaseError handling."""
        mock_service = Mock()
        mock_service.recommend_players = AsyncMock(
            side_effect=UseCaseError("Cannot process request")
        )
        
        request = Mock()
        request.player_ids = [12345]
        
        with pytest.raises(HTTPException) as exc_info:
            await recommend_players(request, mock_service)
        
        assert exc_info.value.status_code == 422
        assert "Cannot process request" in exc_info.value.detail
