from fastapi import APIRouter, Query, status, Depends
from models.players import (
    PlayerSearchResult, 
    AddPlayerResponse, 
    DeletePlayerResponse, 
    SavedPlayer, 
    PlayerDetail,
    RosterAvgRequest,
    RosterAvgResponse
)
# player search
from services.player_search_service import PlayerSearchService

# REMOVE THIS LATER FOR THE SAVED PLAYER
from services.saved_players_service import saved_players_service

# roster average
from services.roster_avg_service import RosterAvgService

from middleware.auth import get_current_user
from typing import List
from dependency.dependencies import get_player_search_service, get_roster_avg_service

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/search", response_model=List[PlayerSearchResult], tags=["search"])
async def search_players(q: str = Query(..., description="Search query for player name"), 
    player_service: PlayerSearchService = Depends(get_player_search_service)):
    """Search for players by name using fuzzy matching (public - no auth required)"""
    return await player_service.search(q)

@router.post("/saved", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED, tags=["saved"])
async def add_saved_player(player_info: dict, current_user: str = Depends(get_current_user)):
    """Add a player to the current user's saved players collection"""
    return await saved_players_service.add_player(current_user, player_info)

@router.get("/saved", response_model=List[SavedPlayer], tags=["saved"])
async def get_saved_players(current_user: str = Depends(get_current_user)):
    """Get all saved players for the current user"""
    return await saved_players_service.get_all_players(current_user)

@router.post("/roster-averages", response_model=RosterAvgResponse, tags=["stats"])
async def get_roster_averages(request: RosterAvgRequest, roster_avg_service: RosterAvgService = Depends(get_roster_avg_service)):
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

@router.get("/{player_id}/detail", response_model=PlayerDetail, tags=["search"])
async def get_player_detail(player_id: int, player_service: PlayerSearchService = Depends(get_player_search_service)):
    """Get detailed information for a specific player (public - no auth required)"""
    return await player_service.get_player_detail(player_id)

@router.get("/saved/{player_id}", response_model=SavedPlayer, tags=["saved"])
async def get_saved_player(player_id: str, current_user: str = Depends(get_current_user)):
    """Get a specific saved player for the current user"""
    return await saved_players_service.get_player(current_user, player_id)

@router.delete("/saved/{player_id}", response_model=DeletePlayerResponse, tags=["saved"])
async def delete_saved_player(player_id: str, current_user: str = Depends(get_current_user)):
    """Delete a player from the current user's saved players collection"""
    return await saved_players_service.delete_player(current_user, player_id)


