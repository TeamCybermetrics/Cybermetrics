"""
Unit tests for players routes.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from routes.players import (
    search_players,
    add_saved_player,
    get_saved_players,
    get_roster_averages,
    get_roster_weakness_scores,
    get_player_value_score,
    get_team_value_scores,
    get_player_detail,
    get_saved_player,
    delete_saved_player,
    update_saved_player_position,
)
from useCaseHelpers.errors import (
    InputValidationError,
    QueryError,
    DatabaseError,
    ConflictError,
    UseCaseError,
)


class TestSearchPlayersRoute:
    """Tests for search_players route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_players_success(self):
        """Test successful player search."""
        mock_service = Mock()
        mock_service.search = AsyncMock(return_value=[{"id": 1, "name": "Player 1"}])
        
        result = await search_players("test", mock_service)
        
        assert len(result) == 1
        mock_service.search.assert_called_once_with("test")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_players_input_validation_error(self):
        """Test search with invalid input."""
        mock_service = Mock()
        mock_service.search = AsyncMock(side_effect=InputValidationError("Invalid query"))
        
        with pytest.raises(HTTPException) as exc_info:
            await search_players("", mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_players_query_error(self):
        """Test search with query error."""
        mock_service = Mock()
        mock_service.search = AsyncMock(side_effect=QueryError("No results"))
        
        with pytest.raises(HTTPException) as exc_info:
            await search_players("test", mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_players_database_error(self):
        """Test search with database error."""
        mock_service = Mock()
        mock_service.search = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await search_players("test", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_players_use_case_error(self):
        """Test search with use case error."""
        mock_service = Mock()
        mock_service.search = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await search_players("test", mock_service)
        
        assert exc_info.value.status_code == 422


class TestAddSavedPlayerRoute:
    """Tests for add_saved_player route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_saved_player_success(self):
        """Test successfully adding a saved player."""
        mock_service = Mock()
        mock_service.add_player = AsyncMock(return_value={"message": "Player added"})
        
        result = await add_saved_player({"id": 123}, "user123", mock_service)
        
        assert result["message"] == "Player added"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_saved_player_input_validation_error(self):
        """Test add with invalid input."""
        mock_service = Mock()
        mock_service.add_player = AsyncMock(side_effect=InputValidationError("Invalid player"))
        
        with pytest.raises(HTTPException) as exc_info:
            await add_saved_player({}, "user123", mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_saved_player_conflict_error(self):
        """Test add with conflict error."""
        mock_service = Mock()
        mock_service.add_player = AsyncMock(side_effect=ConflictError("Player already saved"))
        
        with pytest.raises(HTTPException) as exc_info:
            await add_saved_player({"id": 123}, "user123", mock_service)
        
        assert exc_info.value.status_code == 409
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_saved_player_database_error(self):
        """Test add with database error."""
        mock_service = Mock()
        mock_service.add_player = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await add_saved_player({"id": 123}, "user123", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_saved_player_use_case_error(self):
        """Test add with use case error."""
        mock_service = Mock()
        mock_service.add_player = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await add_saved_player({"id": 123}, "user123", mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetSavedPlayersRoute:
    """Tests for get_saved_players route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_players_success(self):
        """Test getting saved players."""
        mock_service = Mock()
        mock_service.get_all_players = AsyncMock(return_value=[{"id": 1}])
        
        result = await get_saved_players("user123", mock_service)
        
        assert len(result) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_players_database_error(self):
        """Test get with database error."""
        mock_service = Mock()
        mock_service.get_all_players = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_saved_players("user123", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_players_use_case_error(self):
        """Test get with use case error."""
        mock_service = Mock()
        mock_service.get_all_players = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_saved_players("user123", mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetRosterAveragesRoute:
    """Tests for get_roster_averages route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_success(self):
        """Test getting roster averages."""
        mock_service = Mock()
        mock_service.get_roster_averages = AsyncMock(return_value={"avg": 0.250})
        
        request = Mock()
        request.player_ids = [123, 456]
        
        result = await get_roster_averages(request, mock_service)
        
        assert result["avg"] == 0.250
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_input_validation_error(self):
        """Test roster averages with invalid input."""
        mock_service = Mock()
        mock_service.get_roster_averages = AsyncMock(side_effect=InputValidationError("Invalid IDs"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_averages(Mock(), mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_database_error(self):
        """Test roster averages with database error."""
        mock_service = Mock()
        mock_service.get_roster_averages = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_averages(Mock(), mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_use_case_error(self):
        """Test roster averages with use case error."""
        mock_service = Mock()
        mock_service.get_roster_averages = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_averages(Mock(), mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetRosterWeaknessScoresRoute:
    """Tests for get_roster_weakness_scores route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_weakness_scores_success(self):
        """Test getting weakness scores."""
        mock_service = Mock()
        mock_service.get_team_weakness_scores = AsyncMock(return_value={"weakness": 0.5})
        
        request = Mock()
        request.player_ids = [123]
        
        result = await get_roster_weakness_scores(request, mock_service)
        
        assert result["weakness"] == 0.5
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_weakness_scores_input_validation_error(self):
        """Test weakness scores with invalid input."""
        mock_service = Mock()
        mock_service.get_team_weakness_scores = AsyncMock(side_effect=InputValidationError("Invalid"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_weakness_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_weakness_scores_database_error(self):
        """Test weakness scores with database error."""
        mock_service = Mock()
        mock_service.get_team_weakness_scores = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_weakness_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_weakness_scores_use_case_error(self):
        """Test weakness scores with use case error."""
        mock_service = Mock()
        mock_service.get_team_weakness_scores = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_roster_weakness_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetPlayerValueScoreRoute:
    """Tests for get_player_value_score route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_value_score_success(self):
        """Test getting player value score."""
        mock_service = Mock()
        mock_service.get_value_score = AsyncMock(return_value={"score": 95.0})
        
        request = Mock()
        request.model_dump.return_value = {"weakness": {}}
        
        result = await get_player_value_score(123, request, mock_service)
        
        assert result["score"] == 95.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_value_score_input_validation_error(self):
        """Test value score with invalid input."""
        mock_service = Mock()
        mock_service.get_value_score = AsyncMock(side_effect=InputValidationError("Invalid"))
        
        request = Mock()
        request.model_dump.return_value = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_value_score(123, request, mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_value_score_query_error(self):
        """Test value score with query error."""
        mock_service = Mock()
        mock_service.get_value_score = AsyncMock(side_effect=QueryError("Player not found"))
        
        request = Mock()
        request.model_dump.return_value = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_value_score(123, request, mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_value_score_database_error(self):
        """Test value score with database error."""
        mock_service = Mock()
        mock_service.get_value_score = AsyncMock(side_effect=DatabaseError("DB error"))
        
        request = Mock()
        request.model_dump.return_value = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_value_score(123, request, mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_value_score_use_case_error(self):
        """Test value score with use case error."""
        mock_service = Mock()
        mock_service.get_value_score = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        request = Mock()
        request.model_dump.return_value = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_value_score(123, request, mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetTeamValueScoresRoute:
    """Tests for get_team_value_scores route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_success(self):
        """Test getting team value scores."""
        mock_service = Mock()
        mock_service.get_team_value_scores = AsyncMock(return_value=[{"id": 1, "score": 90}])
        
        request = Mock()
        request.player_ids = [123]
        
        result = await get_team_value_scores(request, mock_service)
        
        assert len(result) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_input_validation_error(self):
        """Test team value scores with invalid input."""
        mock_service = Mock()
        mock_service.get_team_value_scores = AsyncMock(side_effect=InputValidationError("Invalid"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_team_value_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_database_error(self):
        """Test team value scores with database error."""
        mock_service = Mock()
        mock_service.get_team_value_scores = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_team_value_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_use_case_error(self):
        """Test team value scores with use case error."""
        mock_service = Mock()
        mock_service.get_team_value_scores = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_team_value_scores(Mock(), mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetPlayerDetailRoute:
    """Tests for get_player_detail route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_success(self):
        """Test getting player detail."""
        mock_service = Mock()
        mock_service.get_player_detail = AsyncMock(return_value={"id": 123, "name": "Player"})
        
        result = await get_player_detail(123, mock_service)
        
        assert result["id"] == 123
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_input_validation_error(self):
        """Test player detail with invalid input."""
        mock_service = Mock()
        mock_service.get_player_detail = AsyncMock(side_effect=InputValidationError("Invalid ID"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_detail(0, mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_query_error(self):
        """Test player detail with query error."""
        mock_service = Mock()
        mock_service.get_player_detail = AsyncMock(side_effect=QueryError("Not found"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_detail(999, mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_database_error(self):
        """Test player detail with database error."""
        mock_service = Mock()
        mock_service.get_player_detail = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_detail(123, mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_player_detail_use_case_error(self):
        """Test player detail with use case error."""
        mock_service = Mock()
        mock_service.get_player_detail = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_player_detail(123, mock_service)
        
        assert exc_info.value.status_code == 422


class TestGetSavedPlayerRoute:
    """Tests for get_saved_player route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_player_success(self):
        """Test getting a saved player."""
        mock_service = Mock()
        mock_service.get_player = AsyncMock(return_value={"id": "123"})
        
        result = await get_saved_player("123", "user123", mock_service)
        
        assert result["id"] == "123"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_player_query_error(self):
        """Test get saved player with query error."""
        mock_service = Mock()
        mock_service.get_player = AsyncMock(side_effect=QueryError("Not found"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_saved_player("999", "user123", mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_player_database_error(self):
        """Test get saved player with database error."""
        mock_service = Mock()
        mock_service.get_player = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_saved_player("123", "user123", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_saved_player_use_case_error(self):
        """Test get saved player with use case error."""
        mock_service = Mock()
        mock_service.get_player = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_saved_player("123", "user123", mock_service)
        
        assert exc_info.value.status_code == 422


class TestDeleteSavedPlayerRoute:
    """Tests for delete_saved_player route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_saved_player_success(self):
        """Test deleting a saved player."""
        mock_service = Mock()
        mock_service.delete_player = AsyncMock(return_value={"message": "Deleted"})
        
        result = await delete_saved_player("123", "user123", mock_service)
        
        assert result["message"] == "Deleted"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_saved_player_query_error(self):
        """Test delete with query error."""
        mock_service = Mock()
        mock_service.delete_player = AsyncMock(side_effect=QueryError("Not found"))
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_saved_player("999", "user123", mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_saved_player_database_error(self):
        """Test delete with database error."""
        mock_service = Mock()
        mock_service.delete_player = AsyncMock(side_effect=DatabaseError("DB error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_saved_player("123", "user123", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_saved_player_use_case_error(self):
        """Test delete with use case error."""
        mock_service = Mock()
        mock_service.delete_player = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_saved_player("123", "user123", mock_service)
        
        assert exc_info.value.status_code == 422


class TestUpdateSavedPlayerPositionRoute:
    """Tests for update_saved_player_position route."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_saved_player_position_success(self):
        """Test updating player position."""
        mock_service = Mock()
        mock_service.update_player_position = AsyncMock(return_value={"id": "123", "position": "1B"})
        
        request = Mock()
        request.position = "1B"
        
        result = await update_saved_player_position("123", request, "user123", mock_service)
        
        assert result["position"] == "1B"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_saved_player_position_input_validation_error(self):
        """Test update with invalid input."""
        mock_service = Mock()
        mock_service.update_player_position = AsyncMock(side_effect=InputValidationError("Invalid position"))
        
        request = Mock()
        request.position = "INVALID"
        
        with pytest.raises(HTTPException) as exc_info:
            await update_saved_player_position("123", request, "user123", mock_service)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_saved_player_position_query_error(self):
        """Test update with query error."""
        mock_service = Mock()
        mock_service.update_player_position = AsyncMock(side_effect=QueryError("Not found"))
        
        request = Mock()
        request.position = "1B"
        
        with pytest.raises(HTTPException) as exc_info:
            await update_saved_player_position("999", request, "user123", mock_service)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_saved_player_position_database_error(self):
        """Test update with database error."""
        mock_service = Mock()
        mock_service.update_player_position = AsyncMock(side_effect=DatabaseError("DB error"))
        
        request = Mock()
        request.position = "1B"
        
        with pytest.raises(HTTPException) as exc_info:
            await update_saved_player_position("123", request, "user123", mock_service)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_saved_player_position_use_case_error(self):
        """Test update with use case error."""
        mock_service = Mock()
        mock_service.update_player_position = AsyncMock(side_effect=UseCaseError("Use case error"))
        
        request = Mock()
        request.position = "1B"
        
        with pytest.raises(HTTPException) as exc_info:
            await update_saved_player_position("123", request, "user123", mock_service)
        
        assert exc_info.value.status_code == 422
