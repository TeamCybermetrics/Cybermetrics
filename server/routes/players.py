from fastapi import APIRouter, Query, status, Depends
from models.players import PlayerSearchResult, AddPlayerResponse, DeletePlayerResponse, SavedPlayer, PlayerDetail
from services.player_search_service import player_search_service
from services.saved_players_service import saved_players_service
from middleware.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/search", response_model=List[PlayerSearchResult], tags=["search"])
async def search_players(q: str = Query(..., description="Search query for player name")):
    """Search for players by name using fuzzy matching (public - no auth required)"""
    return await player_search_service.search(q)

@router.get("/{player_id}/detail", response_model=PlayerDetail, tags=["search"])
async def get_player_detail(player_id: int):
    """Get detailed information for a specific player (public - no auth required)"""
    return await player_search_service.get_player_detail(player_id)

@router.post("/saved", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED, tags=["saved"])
async def add_saved_player(player_info: dict, current_user: str = Depends(get_current_user)):
    """Add a player to the current user's saved players collection"""
    return await saved_players_service.add_player(current_user, player_info)

@router.get("/saved", response_model=List[SavedPlayer], tags=["saved"])
async def get_saved_players(current_user: str = Depends(get_current_user)):
    """Get all saved players for the current user"""
    return await saved_players_service.get_all_players(current_user)

@router.get("/saved/{player_id}", response_model=SavedPlayer, tags=["saved"])
async def get_saved_player(player_id: str, current_user: str = Depends(get_current_user)):
    """Get a specific saved player for the current user"""
    return await saved_players_service.get_player(current_user, player_id)

@router.delete("/saved/{player_id}", response_model=DeletePlayerResponse, tags=["saved"])
async def delete_saved_player(player_id: str, current_user: str = Depends(get_current_user)):
    """Delete a player from the current user's saved players collection"""
    return await saved_players_service.delete_player(current_user, player_id)
