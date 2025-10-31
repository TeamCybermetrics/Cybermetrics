from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from models.players import SavedPlayer, AddPlayerResponse, DeletePlayerResponse, ImportPlayerError

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

    @abstractmethod
    async def import_players(
        self,
        user_id: str,
        players: List[Tuple[int, str, Dict[str, Any]]]
    ) -> Tuple[int, List[ImportPlayerError]]:
        """Bulk import players for a user given validated payloads"""
        pass



    
