from abc import ABC, abstractmethod
from typing import Optional

from domain.team_builder_domain import SaveLineupRequest, SavedLineupModel


class TeamBuilderRepository(ABC):
    """Abstract repository for persisting a user's active lineup."""

    @abstractmethod
    async def get_current_lineup(self, user_id: str) -> Optional[SavedLineupModel]:
        """Return the user's current saved lineup, if any."""
        raise NotImplementedError

    @abstractmethod
    async def save_current_lineup(
        self, user_id: str, payload: SaveLineupRequest
    ) -> SavedLineupModel:
        """Create or update the user's current lineup."""
        raise NotImplementedError

    @abstractmethod
    async def delete_current_lineup(self, user_id: str) -> None:
        """Remove the saved lineup for the given user (noop if none exists)."""
        raise NotImplementedError


__all__ = ["TeamBuilderRepository"]
