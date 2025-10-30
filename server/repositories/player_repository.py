from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class PlayerRepository(ABC):
    @abstractmethod
    async def get_all_players(self) -> List[Dict]:
        """Get all players from database"""
        pass
    
    @abstractmethod
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get a specific mlbplayer by ID"""
        pass
