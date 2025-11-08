from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from domain.team_builder_domain import POSITION_ORDER, DiamondPosition


class LineupSlotPayload(BaseModel):
    """Payload describing a single player assigned to a position."""

    player_id: int = Field(..., description="Unique identifier for the player")
    name: Optional[str] = Field(
        default=None, description="Display name snapshot for the player"
    )
    image_url: Optional[str] = Field(
        default=None, description="Optional image URL for quick rendering"
    )
    years_active: Optional[str] = Field(
        default=None, description="Optional years active text"
    )


class LineupFiltersPayload(BaseModel):
    """Filters associated with a saved lineup."""

    salary_range: Tuple[int, int] = Field(
        default=(0, 100_000_000), description="Min/max salary filter"
    )
    selected_positions: List[DiamondPosition] = Field(
        default_factory=lambda: list(POSITION_ORDER),
        description="Positions currently toggled on in the UI",
    )


class SaveLineupPayload(BaseModel):
    """Incoming request body for saving a lineup."""

    name: str = Field(..., min_length=1, max_length=80)
    lineup: Dict[DiamondPosition, Optional[LineupSlotPayload]]
    filters: LineupFiltersPayload = Field(default_factory=LineupFiltersPayload)
    team_score: Optional[float] = None
    team_budget: Optional[float] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class SavedLineup(BaseModel):
    """Shape returned to the client when a lineup is retrieved."""

    id: str
    name: str
    lineup: Dict[DiamondPosition, Optional[LineupSlotPayload]]
    filters: LineupFiltersPayload
    team_score: Optional[float] = None
    team_budget: Optional[float] = None
    notes: Optional[str] = None
    saved_at: datetime
    updated_at: datetime


class LineupResponse(BaseModel):
    """Envelope used by GET/POST endpoints."""

    lineup: Optional[SavedLineup]


class DeleteLineupResponse(BaseModel):
    message: str = "Lineup deleted"
