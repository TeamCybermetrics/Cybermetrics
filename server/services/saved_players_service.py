from repositories.saved_players_repository import SavedPlayersRepository
from useCaseHelpers.saved_players_helper import SavedPlayersDomain
from dtos.saved_player_dtos import AddPlayerResponse, DeletePlayerResponse
from entities.players import SavedPlayer
from typing import List

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

    async def update_player_position(
        self,
        user_id: str,
        player_id: str,
        position: object,
    ) -> SavedPlayer:
        """Assign or clear a saved player's lineup position."""
        validated_player_id = self.saved_players_domain.validate_player_id(player_id)
        normalized_position = self.saved_players_domain.normalize_position(position)
        return await self.saved_players_repository.update_position(
            user_id,
            validated_player_id,
            normalized_position,
        )


