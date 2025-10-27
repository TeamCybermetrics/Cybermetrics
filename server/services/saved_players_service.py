import logging
from fastapi import HTTPException, status
from repositories.saved_players_repository import SavedPlayersRepository
from domain.saved_players_domain import SavedPlayersDomain
from models.players import (
    AddPlayerResponse,
    DeletePlayerResponse,
    SavedPlayer,
    ImportPlayersResponse,
    ImportPlayerError
)
from typing import List, Tuple, Dict, Any
logger = logging.getLogger(__name__)


class SavedPlayersService:
    """Service for managing user's saved players in Firestore"""

    def __init__(self, saved_players_repository: SavedPlayersRepository, saved_players_domain: SavedPlayersDomain):
        self.saved_players_repository = saved_players_repository
        self.saved_players_domain = saved_players_domain

    async def add_player(self, user_id: str, player_info: dict) -> AddPlayerResponse:
        """Add a player to user's saved players collection"""
        player_id = self.saved_players_domain.validate_player_info(player_info)
        player_response = await self.saved_players_repository.add_player(user_id, player_info, player_id)
        return player_response

    async def get_all_players(self, user_id: str) -> List[SavedPlayer]:
        """Get all saved players for a specific user"""
        saved_players = await self.saved_players_repository.get_all_players(user_id)
        return saved_players

    async def get_player(self, user_id: str, player_id: str) -> SavedPlayer:
        """Get a specific saved player for a user"""
        player = await self.saved_players_repository.get_player(user_id, player_id)
        return player

    async def delete_player(self, user_id: str, player_id: str) -> DeletePlayerResponse:
        """Delete a player from user's saved players collection"""
        player_response = await self.saved_players_repository.delete_player(user_id, player_id)
        return player_response

    async def import_players(self, user_id: str, players: List[Tuple[int, Dict[str, Any]]]) -> ImportPlayersResponse:
        """Bulk import players for a user from parsed CSV data"""
        total_rows = len(players)
        if total_rows == 0:
            return ImportPlayersResponse(
                message="No player rows to import",
                imported=0,
                total_rows=0,
                skipped=[]
            )

        skipped: List[ImportPlayerError] = []
        validated_players: List[Tuple[int, str, Dict[str, Any]]] = []

        for row_index, player_data in players:
            try:
                player_id = self.saved_players_domain.validate_player_info(player_data)
            except HTTPException as exc:
                skipped.append(ImportPlayerError(row=row_index, reason=str(exc.detail)))
                continue
            except Exception:
                skipped.append(ImportPlayerError(row=row_index, reason="Invalid player payload"))
                continue

            validated_players.append((row_index, str(player_id), player_data))

        if not validated_players:
            return ImportPlayersResponse(
                message="CSV import completed",
                imported=0,
                total_rows=total_rows,
                skipped=skipped
            )

        try:
            imported, repository_skipped = await self.saved_players_repository.import_players(user_id, validated_players)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Failed to import players")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to import players"
            ) from exc

        combined_skipped = skipped + repository_skipped

        return ImportPlayersResponse(
            message="CSV import completed",
            imported=imported,
            total_rows=total_rows,
            skipped=combined_skipped
        )
