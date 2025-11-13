from repositories.saved_players_repository import SavedPlayersRepository
from dtos.saved_player_dtos import AddPlayerResponse, DeletePlayerResponse
from entities.players import SavedPlayer
from fastapi import HTTPException, status
from typing import List, Optional
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
        """Retrieve a specific player by ID for a user in there saved section"""
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
        """Delete a specific player by ID for a user in there saved section"""
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

    def _update_position_blocking(
        self,
        user_id: str,
        player_id: str,
        position: Optional[str],
    ) -> SavedPlayer:
        collection = self.db.collection('users').document(user_id).collection('saved_players')
        doc_ref = collection.document(player_id)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found",
            )
        doc_ref.update({"position": position})
        updated_snapshot = doc_ref.get()
        return SavedPlayer(**updated_snapshot.to_dict())

    async def update_position(
        self,
        user_id: str,
        player_id: str,
        position: Optional[str],
    ) -> SavedPlayer:
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )
        try:
            return await to_thread.run_sync(
                self._update_position_blocking,
                user_id,
                player_id,
                position,
            )
        except HTTPException:
            raise
        except Exception as exc:
            self._logger.exception(
                "Failed to update position for player %s (user %s)",
                player_id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update player position",
            ) from exc

