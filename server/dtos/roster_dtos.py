from pydantic import BaseModel, Field
from typing import Dict, List

class RosterAvgRequest(BaseModel):
    """DTO: Request model for roster average stats"""
    player_ids: List[int] = Field(..., min_items=1, description="List of MLB player IDs (mlbam_id)")

class PlayerAvgStats(BaseModel):
    """DTO: Average statistics for a single player"""
    strikeout_rate: float = Field(..., description="Career average strikeout rate (K%)")
    walk_rate: float = Field(..., description="Career average walk rate (BB%)")
    isolated_power: float = Field(..., description="Career average isolated power (ISO)")
    on_base_percentage: float = Field(..., description="Career average on-base percentage (OBP)")
    base_running: float = Field(..., description="Career average base running value (BsR)")

class RosterAvgResponse(BaseModel):
    """DTO: Response model for roster average stats"""
    stats: Dict[int, PlayerAvgStats] = Field(..., description="Dictionary mapping player_id to their average stats")
    total_players: int = Field(..., description="Total number of players with stats returned")

class TeamWeaknessResponse(BaseModel):
    """DTO: Normalized weakness scores per stat (higher = more weakness vs league)"""
    strikeout_rate: float
    walk_rate: float
    isolated_power: float
    on_base_percentage: float
    base_running: float

class ValueScoreRequest(BaseModel):
    """DTO: Request body for computing a player's value score.

    Accepts root-level per-stat weakness weights, e.g.:
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

class ValueScoreResponse(BaseModel):
    """DTO: Response for player value score calculation"""
    latest_war: float
    adjustment_score: float
    value_score: float
    contributions: Dict[str, float]

class PlayerValueScore(BaseModel):
    """DTO: Minimal view for team value-score listing"""
    id: int
    name: str
    adjustment_score: float
    value_score: float
