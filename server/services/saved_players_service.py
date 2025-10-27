import logging
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
from anyio import to_thread


logger = logging.getLogger(__name__)


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
        current_batch_rows: List[Tuple[int, str]] = []

        try:
            for row_index, player_data in players:
                try:
                    player_id = self.saved_players_domain.validate_player_info(player_data)
                except HTTPException as exc:
                    skipped.append(ImportPlayerError(row=row_index, reason=str(exc.detail)))
                    continue
                except Exception:
                    skipped.append(ImportPlayerError(row=row_index, reason="Invalid player payload"))
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
                    batch_ops += 1
                    current_batch_rows.append((row_index, doc_id))

                    if batch_ops >= 450:
                        try:
                            await to_thread.run_sync(batch.commit)
                            imported += len(current_batch_rows)
                        except Exception:
                            logger.exception("Batch commit failed while importing saved players")
                            for failed_row, failed_player_id in current_batch_rows:
                                skipped.append(
                                    ImportPlayerError(
                                        row=failed_row,
                                        player_id=failed_player_id,
                                        reason="Batch commit failed"
                                    )
                                )
                        finally:
                            batch = self.db.batch()
                            batch_ops = 0
                            current_batch_rows.clear()
                except Exception as e:
                    logger.exception("Failed to queue player import write")
                    skipped.append(
                        ImportPlayerError(
                            row=row_index,
                            player_id=str(player_id),
                            reason="Failed to queue write"
                        )
                    )

            if batch_ops:
                try:
                    await to_thread.run_sync(batch.commit)
                    imported += len(current_batch_rows)
                except Exception:
                    logger.exception("Batch commit failed while importing saved players")
                    for failed_row, failed_player_id in current_batch_rows:
                        skipped.append(
                            ImportPlayerError(
                                row=failed_row,
                                player_id=failed_player_id,
                                reason="Batch commit failed"
                            )
                        )
                finally:
                    batch = self.db.batch()
                    batch_ops = 0
                    current_batch_rows.clear()

            return ImportPlayersResponse(
                message="CSV import completed",
                imported=imported,
                total_rows=total_rows,
                skipped=skipped
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to import players")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to import players"
            ) from e
