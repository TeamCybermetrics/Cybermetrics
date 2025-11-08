from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


DiamondPosition = Literal["LF", "CF", "RF", "3B", "SS", "2B", "1B", "P", "C", "DH"]
POSITION_ORDER: Tuple[DiamondPosition, ...] = (
    "LF",
    "CF",
    "RF",
    "3B",
    "SS",
    "2B",
    "1B",
    "P",
    "C",
    "DH",
)

MAX_LINEUPS_PER_USER = 20
MAX_SALARY = 100_000_000


class LineupSlotModel(BaseModel):
    """Snapshot of a player assigned to a lineup position."""

    model_config = ConfigDict(extra="allow")

    player_id: int = Field(..., gt=0)
    name: Optional[str] = Field(default=None, max_length=120)
    image_url: Optional[str] = Field(default=None, max_length=500)
    years_active: Optional[str] = Field(default=None, max_length=50)


class LineupFiltersModel(BaseModel):
    """User-defined filters that accompany a saved lineup."""

    salary_range: Tuple[int, int] = Field(default=(0, MAX_SALARY))
    selected_positions: List[DiamondPosition] = Field(
        default_factory=lambda: list(POSITION_ORDER)
    )

    @field_validator("salary_range")
    @classmethod
    def validate_salary_range(cls, value: Tuple[int, int]) -> Tuple[int, int]:
        minimum, maximum = value
        if minimum < 0 or maximum > MAX_SALARY:
            raise ValueError(f"Salary range must be between 0 and {MAX_SALARY}")
        if minimum > maximum:
            raise ValueError("Minimum salary cannot exceed maximum salary")
        return minimum, maximum

    @field_validator("selected_positions")
    @classmethod
    def deduplicate_positions(cls, value: List[DiamondPosition]) -> List[DiamondPosition]:
        seen = set()
        ordered: List[DiamondPosition] = []
        for position in value:
            if position not in seen:
                seen.add(position)
                ordered.append(position)
        return ordered


class LineupMapModel(BaseModel):
    """Mapping of every diamond position to an optional player slot."""

    lineup: Dict[DiamondPosition, Optional[LineupSlotModel]] = Field(
        default_factory=dict
    )

    @model_validator(mode="before")
    @classmethod
    def ensure_all_positions(cls, values: Dict) -> Dict:
        lineup = values.get("lineup", {}) if isinstance(values, dict) else {}
        for position in POSITION_ORDER:
            lineup.setdefault(position, None)
        values["lineup"] = lineup
        return values

    @model_validator(mode="after")
    def ensure_unique_players(self) -> "LineupMapModel":
        seen_ids = set()
        duplicates = []
        for slot in self.lineup.values():
            if slot is None:
                continue
            player_id = slot.player_id
            if player_id in seen_ids:
                duplicates.append(player_id)
            else:
                seen_ids.add(player_id)

        if duplicates:
            raise ValueError(
                f"Players cannot occupy more than one position: {sorted(set(duplicates))}"
            )
        return self


class SaveLineupRequest(BaseModel):
    """Request payload for creating or updating a lineup."""

    lineup_id: Optional[str] = Field(
        default=None, description="Existing lineup id when performing an update"
    )
    name: str = Field(..., min_length=1, max_length=80)
    lineup: LineupMapModel
    filters: LineupFiltersModel = Field(default_factory=LineupFiltersModel)
    team_score: Optional[float] = None
    team_budget: Optional[float] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    is_current: bool = False

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Lineup name cannot be empty")
        return normalized

    @model_validator(mode="after")
    def ensure_not_empty(self) -> "SaveLineupRequest":
        has_player = any(slot is not None for slot in self.lineup.lineup.values())
        if not has_player:
            raise ValueError("At least one position must be filled before saving a lineup")
        return self


class SavedLineupModel(SaveLineupRequest):
    """Representation of a lineup persisted in Firestore."""

    id: str
    saved_at: datetime
    updated_at: datetime

    def snapshot(self) -> Dict:
        """Convert the model into a serializable dict for storage."""
        return {
            "name": self.name,
            "lineup": self.lineup.model_dump(mode="json"),
            "filters": self.filters.model_dump(mode="json"),
            "team_score": self.team_score,
            "team_budget": self.team_budget,
            "notes": self.notes,
            "is_current": self.is_current,
            "saved_at": self.saved_at,
            "updated_at": self.updated_at,
        }


def enforce_lineup_quota(current_count: int, limit: int = MAX_LINEUPS_PER_USER) -> None:
    """Raise an error if the user has exceeded the saved lineup quota."""
    if current_count >= limit:
        raise ValueError(f"Maximum of {limit} saved lineups reached")


def ensure_unique_lineup_name(
    name: str, existing_lineup_names: Dict[str, str], ignore_lineup_id: Optional[str] = None
) -> None:
    """
    Ensure the incoming name does not collide with existing ones.

    Names are compared case-insensitively; when updating, the lineup being updated can be ignored.
    """

    normalized = name.lower()
    for lineup_id, existing_name in existing_lineup_names.items():
        if ignore_lineup_id and lineup_id == ignore_lineup_id:
            continue
        if existing_name.lower() == normalized:
            raise ValueError("Lineup name must be unique per user")


__all__ = [
    "DiamondPosition",
    "LineupSlotModel",
    "LineupFiltersModel",
    "LineupMapModel",
    "SaveLineupRequest",
    "SavedLineupModel",
    "MAX_LINEUPS_PER_USER",
    "enforce_lineup_quota",
    "ensure_unique_lineup_name",
]
