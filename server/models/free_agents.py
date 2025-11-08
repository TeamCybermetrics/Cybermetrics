from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FreeAgentPlayer(BaseModel):
    """Model for a single free agent player from Sportradar API"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    full_name: str  # This should always be present
    position: Optional[str] = None
    status: str
    mlbam_id: Optional[str] = None  # Not all free agents have MLBAM IDs in the API
    height: Optional[str] = None
    weight: Optional[str] = None
    throw_hand: Optional[str] = None
    bat_hand: Optional[str] = None
    updated: Optional[str] = None  # Some free agents don't have update timestamps
    
    class Config:
        extra = "allow"


class FreeAgentsResponse(BaseModel):
    """Response model for free agents list"""
    league_id: str
    league_name: str
    league_alias: str
    free_agents: List[FreeAgentPlayer]
    total_count: int
    fetched_at: str
    
    class Config:
        extra = "allow"


class StoredFreeAgent(BaseModel):
    """Model for free agent stored in Firebase"""
    mlbam_id: str
    sportradar_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    position: Optional[str] = None
    status: str
    height: Optional[str] = None
    weight: Optional[str] = None
    throw_hand: Optional[str] = None
    bat_hand: Optional[str] = None
    last_updated: str
    stored_at: str
    
    class Config:
        extra = "allow"
