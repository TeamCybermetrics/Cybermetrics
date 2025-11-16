from pydantic import BaseModel, Field
from typing import Dict, List

# ============================================================================
# INPUT DTOs (Requests)
# ============================================================================

class RosterAvgRequest(BaseModel):
    """
    Request to calculate roster average statistics.
    
    Accepts a list of player IDs to compute aggregate
    career statistics across the roster.
    """
    player_ids: List[int] = Field(..., min_items=1, description="List of MLB player IDs (mlbam_id)")

class ValueScoreRequest(BaseModel):
    """
    Request to compute a player's value score.
    
    Accepts per-stat weakness weights to calculate how well
    a player addresses team weaknesses. Each weight represents
    the importance of improving that particular stat.
    
    Example:
    {
        "strikeout_rate": 0.0,
        "walk_rate": 0.0,
        "isolated_power": 0.221,
        "on_base_percentage": 0.066,
        "base_running": 0.764
    }
    """
    strikeout_rate: float = 0.0
    walk_rate: float = 0.0
    isolated_power: float = 0.0
    on_base_percentage: float = 0.0
    base_running: float = 0.0


# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class PlayerAvgStats(BaseModel):
    """
    Average career statistics for a single player.
    
    Contains key offensive metrics averaged across
    the player's career.
    """
    strikeout_rate: float = Field(..., description="Career average strikeout rate (K%)")
    walk_rate: float = Field(..., description="Career average walk rate (BB%)")
    isolated_power: float = Field(..., description="Career average isolated power (ISO)")
    on_base_percentage: float = Field(..., description="Career average on-base percentage (OBP)")
    base_running: float = Field(..., description="Career average base running value (BsR)")

class RosterAvgResponse(BaseModel):
    """
    Response containing roster average statistics.
    
    Maps each player ID to their average career stats,
    allowing for roster-wide analysis.
    """
    stats: Dict[int, PlayerAvgStats] = Field(..., description="Dictionary mapping player_id to their average stats")
    total_players: int = Field(..., description="Total number of players with stats returned")

class TeamWeaknessResponse(BaseModel):
    """
    Normalized team weakness scores per stat.
    
    Lower values indicate greater weakness relative to
    league average. Used to identify areas for improvement.
    """
    strikeout_rate: float
    walk_rate: float
    isolated_power: float
    on_base_percentage: float
    base_running: float

class ValueScoreResponse(BaseModel):
    """
    Response containing a player's value score calculation.
    
    Combines the player's WAR with an adjustment score based
    on how well they address team weaknesses.
    """
    latest_war: float
    adjustment_score: float
    value_score: float
    contributions: Dict[str, float]

class PlayerValueScore(BaseModel):
    """
    Minimal player value score view for listings.
    
    Provides essential information for displaying players
    ranked by their value to the team.
    """
    id: int
    name: str
    adjustment_score: float
    value_score: float
