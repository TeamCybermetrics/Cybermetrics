from fastapi import APIRouter, Query, status, Depends, HTTPException
from dtos.player_dtos import PlayerSearchResult, PlayerDetail
from dtos.saved_player_dtos import AddPlayerResponse, DeletePlayerResponse, UpdateSavedPlayerPositionRequest
from dtos.roster_dtos import (
    RosterAvgRequest,
    RosterAvgResponse,
    TeamWeaknessResponse,
    ValueScoreRequest,
    ValueScoreResponse,
    PlayerValueScore,
)
from entities.players import SavedPlayer
from middleware.auth import get_current_user
from typing import List, Annotated
from dependency.dependencies import get_player_search_service, get_roster_avg_service, get_saved_players_service

# player search
from services.player_search_service import PlayerSearchService

# roster average
from services.roster_avg_service import RosterAvgService

# player save
from services.saved_players_service import SavedPlayersService
from useCaseHelpers.errors import (
    InputValidationError,
    AuthError,
    QueryError,
    DatabaseError,
    DependencyUnavailableError,
    ConflictError,
    UseCaseError,
)

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/search", response_model=List[PlayerSearchResult], tags=["search"])
async def search_players(
    q: Annotated[str, Query(description="Search query for player name")], 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Search for players by name using fuzzy matching (public - no auth required)"""
    try:
        return await player_service.search(q)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.post("/saved", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED, tags=["saved"])
async def add_saved_player(
    player_info: dict, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Add a player to the current user's saved players collection"""
    try:
        return await saved_players_service.add_player(current_user, player_info)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.get("/saved", response_model=List[SavedPlayer], tags=["saved"])
async def get_saved_players(
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get all saved players for the current user"""
    try:
        return await saved_players_service.get_all_players(current_user)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.post("/roster-averages", response_model=RosterAvgResponse, tags=["stats"])
async def get_roster_averages(
    request: RosterAvgRequest, 
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)]
):
    """
    Get career average statistics for multiple players.
    
    Returns the career averages across all seasons for:
    - Strikeout rate (K%)
    - Walk rate (BB%)
    - Isolated power (ISO)
    - On-base percentage (OBP)
    - Base running value (BsR)
    
    Public endpoint - no authentication required.
    """
    try:
        return await roster_avg_service.get_roster_averages(request.player_ids)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.post("/roster-averages/weakness", response_model=TeamWeaknessResponse, tags=["stats"])
async def get_roster_weakness_scores(
    request: RosterAvgRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Return normalized team weakness scores vs league unweighted averages (public)."""
    try:
        return await roster_avg_service.get_team_weakness_scores(request.player_ids)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.post("/{player_id}/value-score", response_model=ValueScoreResponse, tags=["stats"])
async def get_player_value_score(
    player_id: int,
    request: ValueScoreRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Compute a player's value score using latest WAR and team weaknesses (public)."""
    try:
        return await roster_avg_service.get_value_score(player_id, request.model_dump())
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.post("/value-scores", response_model=List[PlayerValueScore], tags=["stats"])
async def get_team_value_scores(
    request: RosterAvgRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Given a list of player IDs, compute team weakness and return each player's id, name, adjustment_score, and value_score."""
    try:
        return await roster_avg_service.get_team_value_scores(request.player_ids)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.get("/{player_id}/detail", response_model=PlayerDetail, tags=["search"])
async def get_player_detail(
    player_id: int, 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Get detailed information for a specific player (public - no auth required)"""
    try:
        return await player_service.get_player_detail(player_id)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.get("/saved/{player_id}", response_model=SavedPlayer, tags=["saved"])
async def get_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get a specific saved player for the current user"""
    try:
        return await saved_players_service.get_player(current_user, player_id)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.delete("/saved/{player_id}", response_model=DeletePlayerResponse, tags=["saved"])
async def delete_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)],
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Delete a player from the current user's saved players collection"""
    try:
        return await saved_players_service.delete_player(current_user, player_id)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.patch(
    "/saved/{player_id}/position",
    response_model=SavedPlayer,
    tags=["saved"],
    status_code=status.HTTP_200_OK,
)
async def update_saved_player_position(
    player_id: str,
    request: UpdateSavedPlayerPositionRequest,
    current_user: Annotated[str, Depends(get_current_user)],
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)],
):
    """Assign or clear a saved player's lineup position for the current user."""
    try:
        return await saved_players_service.update_player_position(
            current_user,
            player_id,
            request.position,
        )
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


