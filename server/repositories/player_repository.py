from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class PlayerRepository(ABC):
    @abstractmethod
    async def get_all_players(self) -> List[Dict]:
        """Get all players from database"""
        pass
    
    @abstractmethod
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get a specific mlbplayer by ID"""
        pass

    @abstractmethod
    def upload_team(self, team, team_name, final_players):
        pass

    @abstractmethod
    def bulk_upsert_players(self, players: List[Dict[str, Any]]) -> None:
        pass