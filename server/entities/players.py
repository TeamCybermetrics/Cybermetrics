from pydantic import BaseModel
from typing import Optional, Dict

class SavedPlayer(BaseModel):
    """Saved player data"""
    id: int
    name: str
    image_url: Optional[str] = None
    years_active: Optional[str] = None
    position: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields from Firestore


class SeasonStats(BaseModel):
    """Stats for a single season"""
    # Basic counting stats
    games: int = 0
    plate_appearances: int = 0
    at_bats: int = 0
    hits: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    runs: int = 0
    rbi: int = 0
    walks: int = 0
    strikeouts: int = 0
    stolen_bases: int = 0
    caught_stealing: int = 0
    
    # Rate stats
    batting_average: float = 0.0
    on_base_percentage: float = 0.0
    slugging_percentage: float = 0.0
    ops: float = 0.0
    isolated_power: float = 0.0
    babip: float = 0.0
    
    # Plate discipline
    walk_rate: float = 0.0
    strikeout_rate: float = 0.0
    bb_k_ratio: float = 0.0
    
    # Advanced metrics
    woba: float = 0.0
    wrc_plus: float = 0.0
    war: float = 0.0
    off: float = 0.0
    def_: float = 0.0  # 'def' is a Python keyword, use def_
    base_running: float = 0.0
    
    # Contact quality (may be None for older seasons)
    hard_hit_rate: Optional[float] = None
    barrel_rate: Optional[float] = None
    avg_exit_velocity: Optional[float] = None
    avg_launch_angle: Optional[float] = None
    
    # Team
    team_abbrev: Optional[str] = None
    
    class Config:
        extra = "allow"



