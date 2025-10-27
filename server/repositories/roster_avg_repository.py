from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from models.players import PlayerAvgStats

class RosterRepository(ABC):
    @abstractmethod
    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """Get seasons data for multiple players"""
        pass