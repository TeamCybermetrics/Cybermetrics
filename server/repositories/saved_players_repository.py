from abc import ABC, abstractmethod
from typing import List, Optional
from models.players import SavedPlayer, AddPlayerResponse, DeletePlayerResponse

class SavedPlayersRepository(ABC):
    @abstractmethod
    async def add_player(self, user_id: str, player_info: dict, player_id: str) -> AddPlayerResponse:
        """Add a player to user's saved players collection"""
        pass
    
    @abstractmethod
    async def get_all_players(self, user_id: str) -> List[SavedPlayer]:
        """Get all saved players for a specific user"""
        pass
    
    @abstractmethod
    async def get_player(self, user_id: str, player_id: str) -> SavedPlayer:
        """Get a specific saved player for a user"""
        pass
    
    @abstractmethod
    async def delete_player(self, user_id: str, player_id: str) -> DeletePlayerResponse:
        """Delete a player from user's saved players collection"""
        pass




    