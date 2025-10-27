from fastapi import HTTPException, status
from repositories.saved_players_repository import SavedPlayersRepository
from domain.saved_players_domain import SavedPlayersDomain
from config.firebase import firebase_service
from models.players import (
    AddPlayerResponse,
    DeletePlayerResponse,
    SavedPlayer,
    ImportPlayersResponse,
    ImportPlayerError
)
from typing import List, Tuple, Dict, Any


class SavedPlayersService:
    """Service for managing user's saved players in Firestore"""

    def __init__(self, saved_players_repository: SavedPlayersRepository, saved_players_domain: SavedPlayersDomain):
        self.saved_players_repository = saved_players_repository
        self.saved_players_domain = saved_players_domain
        self.db = firebase_service.db if hasattr(firebase_service, "db") else None

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
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )

        total_rows = len(players)
        if total_rows == 0:
            return ImportPlayersResponse(
                message="No player rows to import",
                imported=0,
                total_rows=0,
                skipped=[]
            )

        batch = self.db.batch()
        batch_ops = 0
        imported = 0
        skipped: List[ImportPlayerError] = []

        try:
            for row_index, player_data in players:
                player_id = player_data.get("id")

                if player_id is None:
                    skipped.append(ImportPlayerError(row=row_index, reason="Missing player ID"))
                    continue

                try:
                    doc_id = str(player_id)
                    doc_ref = (
                        self.db.collection('users')
                        .document(user_id)
                        .collection('saved_players')
                        .document(doc_id)
                    )
                    batch.set(doc_ref, player_data)
                    imported += 1
                    batch_ops += 1

                    if batch_ops >= 450:
                        batch.commit()
                        batch = self.db.batch()
                        batch_ops = 0
                except Exception as e:
                    skipped.append(
                        ImportPlayerError(
                            row=row_index,
                            player_id=str(player_id),
                            reason=str(e)
                        )
                    )

            if batch_ops:
                batch.commit()

            return ImportPlayersResponse(
                message="CSV import completed",
                imported=imported,
                total_rows=total_rows,
                skipped=skipped
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to import players: {str(e)}"
            )