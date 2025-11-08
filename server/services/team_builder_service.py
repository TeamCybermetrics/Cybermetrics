from fastapi import HTTPException, status

from domain.team_builder_domain import SaveLineupRequest, SavedLineupModel
from repositories.team_builder_repository import TeamBuilderRepository


class TeamBuilderService:
    """Service responsible for orchestrating lineup persistence and retrieval."""

    def __init__(self, repository: TeamBuilderRepository):
        self.repository = repository

    async def get_current_lineup(self, user_id: str) -> SavedLineupModel | None:
        return await self.repository.get_current_lineup(user_id)

    async def save_current_lineup(
        self, user_id: str, payload: SaveLineupRequest
    ) -> SavedLineupModel:
        try:
            return await self.repository.save_current_lineup(user_id, payload)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    async def delete_current_lineup(self, user_id: str) -> None:
        await self.repository.delete_current_lineup(user_id)
