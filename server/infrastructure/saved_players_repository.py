from repositories.saved_players_repository import SavedPlayersRepository
from models.players import SavedPlayer, AddPlayerResponse, DeletePlayerResponse
from fastapi import HTTPException, status
from typing import List
from anyio import to_thread


class SavedPlayersRepositoryFirebase(SavedPlayersRepository):
    def __init__(self, db):
        """Initialize the repository with a Firebase database instance"""
        self.db = db
    
    async def add_player(self, user_id: str, player_info: dict, player_id: str) -> AddPlayerResponse:
        """Add a player to the user's saved players collection"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Save player to user's subcollection in Firestore
            self.db.collection('users').document(user_id).collection('saved_players').document(player_id).set(player_info)
            
            return AddPlayerResponse(
                message="Player data added successfully",
                player_id=player_id
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add player: {str(e)}"
            )
    
    async def get_all_players(self, user_id: str) -> List[SavedPlayer]:
        """Retrieve all saved players for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )

        try:
            players_ref = self.db.collection('users').document(user_id).collection('saved_players').stream()
            saved_players = []
            
            for player_doc in players_ref:
                player_data = player_doc.to_dict()
                saved_players.append(SavedPlayer(**player_data))
            
            return saved_players
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve players: {str(e)}"
            )

    
    async def get_player(self, user_id: str, player_id: str) -> SavedPlayer:
        """Retrieve a specific player by ID for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            player_ref = self.db.collection('users').document(user_id).collection('saved_players').document(player_id)
            player_doc = player_ref.get()
            
            if not player_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with ID {player_id} not found"
                )
            
            return SavedPlayer(**player_doc.to_dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve player: {str(e)}"
            )
    
    async def delete_player(self, user_id: str, player_id: str) -> DeletePlayerResponse:
        """Delete a specific player by ID for a user"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Check if player exists
            player_ref, player_doc = await to_thread.run_sync(fetch_ref_and_doc)
            player_doc = player_ref.get()
            
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete player: {str(e)}"
            )
    
    def fetch_ref_and_doc(self, user_id: str, player_id: str):
        """Gets a reference to Firebase doc and returns it"""
        ref = self.db.collection('users').document(user_id).collection('saved_players').document(player_id)
        return ref, ref.get()

