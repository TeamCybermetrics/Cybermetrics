from pydantic import BaseModel, Field
from typing import Optional

class PlayerSearchResult(BaseModel):
    """Player search result from the index"""
    id: int
    name: str
    score: float
    image_url: str
    years_active: str

class PlayerInfo(BaseModel):
    """Player information to be saved"""
    id: int
    name: str
    # Add any other fields your friend's code might use
    
    class Config:
        extra = "allow"  # Allow additional fields

class AddPlayerRequest(BaseModel):
    """Request model for adding a player"""
    player_info: dict

class AddPlayerResponse(BaseModel):
    """Response after adding a player"""
    message: str
    player_id: str

class DeletePlayerResponse(BaseModel):
    """Response after deleting a player"""
    message: str

class SavedPlayer(BaseModel):
    """Saved player data"""
    id: int
    name: str
    image_url: Optional[str] = None
    years_active: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields from Firestore

class PlayerDetail(BaseModel):
    """Detailed player information"""
    id: int
    name: str
    image_url: str
    years_active: str
    first_name: str
    last_name: str
    mlb_played_first: Optional[str] = None
    mlb_played_last: Optional[str] = None
    key_retro: Optional[str] = None
    key_bbref: Optional[str] = None
    key_fangraphs: Optional[int] = None

