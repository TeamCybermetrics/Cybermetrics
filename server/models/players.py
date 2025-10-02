from pydantic import BaseModel, Field
from typing import Optional

class PlayerSearchResult(BaseModel):
    """Player search result from the index"""
    id: int
    name: str
    score: float

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
    
    class Config:
        extra = "allow"  # Allow additional fields from Firestore

