from pydantic import BaseModel
from typing import Optional, Dict
from entities.players import SeasonStats

# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class PlayerSearchResult(BaseModel):
    """DTO: Player search result from the index"""
    id: int
    name: str
    score: float
    image_url: str
    years_active: str

class PlayerDetail(BaseModel):
    """DTO: Detailed player information with all seasons stats"""
    mlbam_id: int
    fangraphs_id: int
    name: str
    image_url: str
    years_active: str
    team_abbrev: Optional[str] = None
    overall_score: float = 0.0
    seasons: Dict[str, SeasonStats]  # Year -> Stats mapping
    
    class Config:
        extra = "allow"
