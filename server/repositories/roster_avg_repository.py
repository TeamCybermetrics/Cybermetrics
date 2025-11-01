from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from models.players import PlayerAvgStats

class RosterRepository(ABC):
    @abstractmethod
    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """Get seasons data for multiple players"""
        pass

    @abstractmethod
    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """Fetch the league-wide unweighted average stats from Firebase (document: league/averages)."""
        pass