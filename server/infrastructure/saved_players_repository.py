from repositories.saved_players_repository import SavedPlayersRepository
from models.players import SavedPlayer, AddPlayerResponse, DeletePlayerResponse, ImportPlayerError
from fastapi import HTTPException, status
from typing import List, Tuple, Dict, Any
from anyio import to_thread
import logging


class SavedPlayersRepositoryFirebase(SavedPlayersRepository):
    def __init__(self, db):
        """Initialize the repository with a Firebase database instance"""
        self.db = db
        self._logger = logging.getLogger(__name__)
    
    def _add_player_blocking(self, user_id: str, player_info: dict, player_id: str) -> None:
        """Blocking version: Add a player to user's collection"""
        self.db.collection('users').document(user_id).collection('saved_players').document(player_id).set(player_info)
    
    async def add_player(self, user_id: str, player_info: dict, player_id: str) -> AddPlayerResponse:
        """Add a player to the user's saved players collection"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            await to_thread.run_sync(self._add_player_blocking, user_id, player_info, player_id)
            
            return AddPlayerResponse(
                message="Player data added successfully",
                player_id=player_id
            )
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to add player for user: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add player"
            ) from e
    
    def _get_all_players_blocking(self, user_id: str) -> List[SavedPlayer]:
        """Blocking version: Retrieve all saved players for a user"""
        players_ref = self.db.collection('users').document(user_id).collection('saved_players').stream()
        saved_players = []
        
        for player_doc in players_ref:
            player_data = player_doc.to_dict()
            saved_players.append(SavedPlayer(**player_data))
        
        return saved_players
    
    async def get_all_players(self, user_id: str) -> List[SavedPlayer]:
        """Retrieve all saved players for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )

        try:
            saved_players = await to_thread.run_sync(self._get_all_players_blocking, user_id)
            return saved_players
        except Exception as e:
            self._logger.exception("Failed to retrieve players for user: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve players"
            ) from e

    
    async def get_player(self, user_id: str, player_id: str) -> SavedPlayer:
        """Retrieve a specific player by ID for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            player_ref, player_doc = await to_thread.run_sync(
                lambda: self.fetch_ref_and_doc(user_id, player_id)
            )
            
            if not player_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with ID {player_id} not found"
                )
            
            return SavedPlayer(**player_doc.to_dict())
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to retrieve player: %s for user: %s", player_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve player"
            ) from e
    
    async def delete_player(self, user_id: str, player_id: str) -> DeletePlayerResponse:
        """Delete a specific player by ID for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Check if player exists
            player_ref, player_doc = await to_thread.run_sync(
                lambda: self.fetch_ref_and_doc(user_id, player_id)
            )
            
            if not player_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with ID {player_id} not found"
                )
            
            await to_thread.run_sync(player_ref.delete)
            
            return DeletePlayerResponse(
                message="Player deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to delete player: %s for user: %s", player_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete player"
            ) from e
    
    def fetch_ref_and_doc(self, user_id: str, player_id: str):
        """Gets a reference to Firebase doc and returns it"""
        ref = self.db.collection('users').document(user_id).collection('saved_players').document(player_id)
        return ref, ref.get()

    async def import_players(
        self,
        user_id: str,
        players: List[Tuple[int, str, Dict[str, Any]]]
    ) -> Tuple[int, List[ImportPlayerError]]:
        """Bulk import validated player payloads for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )

        batch = self.db.batch()
        batch_ops = 0
        imported = 0
        skipped: List[ImportPlayerError] = []
        current_batch_rows: List[Tuple[int, str]] = []

        async def commit_current_batch(active_batch, rows):
            nonlocal imported
            if not rows:
                return
            try:
                await to_thread.run_sync(active_batch.commit)
                imported += len(rows)
            except Exception:
                self._logger.exception("Batch commit failed while importing saved players")
                for failed_row, failed_player_id in rows:
                    skipped.append(
                        ImportPlayerError(
                            row=failed_row,
                            player_id=failed_player_id,
                            reason="Batch commit failed"
                        )
                    )

        try:
            for row_index, doc_id, player_data in players:
                try:
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
                        await commit_current_batch(batch, current_batch_rows)
                        batch = self.db.batch()
                        batch_ops = 0
                        current_batch_rows.clear()
                except Exception:
                    self._logger.exception("Failed to queue player import write for user: %s", user_id)
                    skipped.append(
                        ImportPlayerError(
                            row=row_index,
                            player_id=doc_id,
                            reason="Failed to queue write"
                        )
                    )

            if batch_ops:
                await commit_current_batch(batch, current_batch_rows)
                current_batch_rows.clear()

            return imported, skipped
        except HTTPException:
            raise
        except Exception as exc:
            self._logger.exception("Failed to import players for user: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to import players"
            ) from exc
