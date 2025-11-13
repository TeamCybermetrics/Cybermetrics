from pydantic import BaseModel
from typing import Optional, Dict
from entities.players import SeasonStats

# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class PlayerSearchResult(BaseModel):
    """
    Player search result from the index.
    
    Contains basic player information with a relevance score
    for search ranking purposes.
    """
    id: int
    name: str
    score: float
    image_url: str
    years_active: str

class PlayerDetail(BaseModel):
    """
    Detailed player information with all seasons stats.
    
    Provides comprehensive player data including historical
    season-by-season statistics.
    """
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
