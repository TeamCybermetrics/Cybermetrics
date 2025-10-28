from fastapi import APIRouter, Query, status, Depends
from models.players import (
    PlayerSearchResult, 
    AddPlayerResponse, 
    DeletePlayerResponse, 
    SavedPlayer, 
    PlayerDetail,
    RosterAvgRequest,
    RosterAvgResponse,
    TeamWeaknessResponse,
    ValueScoreRequest,
    ValueScoreResponse,
    PlayerValueScore,
)
from middleware.auth import get_current_user
from typing import List, Annotated
from dependency.dependencies import get_player_search_service, get_roster_avg_service, get_saved_players_service

# player search
from services.player_search_service import PlayerSearchService

# roster average
from services.roster_avg_service import RosterAvgService

# player save
from services.saved_players_service import SavedPlayersService

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/search", response_model=List[PlayerSearchResult], tags=["search"])
async def search_players(
    q: Annotated[str, Query(description="Search query for player name")], 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Search for players by name using fuzzy matching (public - no auth required)"""
    return await player_service.search(q)

@router.post("/saved", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED, tags=["saved"])
async def add_saved_player(
    player_info: dict, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Add a player to the current user's saved players collection"""
    return await saved_players_service.add_player(current_user, player_info)

@router.get("/saved", response_model=List[SavedPlayer], tags=["saved"])
async def get_saved_players(
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get all saved players for the current user"""
    return await saved_players_service.get_all_players(current_user)

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
    return await roster_avg_service.get_roster_averages(request.player_ids)

@router.post("/roster-averages/weakness", response_model=TeamWeaknessResponse, tags=["stats"])
async def get_roster_weakness_scores(
    request: RosterAvgRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Return normalized team weakness scores vs league unweighted averages (public)."""
    return await roster_avg_service.get_team_weakness_scores(request.player_ids)

@router.post("/{player_id}/value-score", response_model=ValueScoreResponse, tags=["stats"])
async def get_player_value_score(
    player_id: int,
    request: ValueScoreRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Compute a player's value score using latest WAR and team weaknesses (public)."""
    return await roster_avg_service.get_value_score(player_id, request.dict())

@router.post("/value-scores", response_model=List[PlayerValueScore], tags=["stats"])
async def get_team_value_scores(
    request: RosterAvgRequest,
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)],
):
    """Given a list of player IDs, compute team weakness and return each player's id, name, adjustment_score, and value_score."""
    return await roster_avg_service.get_team_value_scores(request.player_ids)

@router.get("/{player_id}/detail", response_model=PlayerDetail, tags=["search"])
async def get_player_detail(
    player_id: int, 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Get detailed information for a specific player (public - no auth required)"""
    return await player_service.get_player_detail(player_id)

@router.get("/saved/{player_id}", response_model=SavedPlayer, tags=["saved"])
async def get_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get a specific saved player for the current user"""
    return await saved_players_service.get_player(current_user, player_id)

@router.delete("/saved/{player_id}", response_model=DeletePlayerResponse, tags=["saved"])
async def delete_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)],
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Delete a player from the current user's saved players collection"""
    return await saved_players_service.delete_player(current_user, player_id)


