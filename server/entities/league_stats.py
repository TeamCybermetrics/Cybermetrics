from typing import Dict, List
from pydantic import BaseModel, Field


class TeamAggregate(BaseModel):
    team_id: str = Field(..., description="Identifier for the team document")
    avg: Dict[str, float] = Field(..., description="Unweighted team average stats")
    player_count: int = Field(..., ge=0, description="Number of players included in team average")


class LeagueAggregate(BaseModel):
    unweighted: Dict[str, float]
    weighted_by_player_count: Dict[str, float]
    unweighted_std: Dict[str, float]
    weighted_by_player_count_std: Dict[str, float]
    teams_counted: int
    players_counted: int
    updated_at: str
