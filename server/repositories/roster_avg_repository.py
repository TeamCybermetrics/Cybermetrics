from abc import ABC, abstractmethod
from typing import Dict, List, Any

class RosterRepository(ABC):
    @abstractmethod
    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """Get seasons data for multiple players"""
        pass

    @abstractmethod
    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """Fetch the league-wide unweighted average stats from Firebase (document: league/averages)."""
        pass

    @abstractmethod
    async def get_league_unweighted_std(self) -> Dict[str, float]:
        """Fetch the league-wide unweighted standard deviations from Firebase (document: league/averages)."""
        pass

    @abstractmethod
    async def get_league_weighted_std(self) -> Dict[str, float]:
        """Fetch the league-wide weighted-by-player-count standard deviations from Firebase (document: league/averages)."""
        pass

    @abstractmethod
    def fetch_team_roster(self, team_id: int, season: int) -> Dict[str, Any]:
        """Fetch active roster metadata for a given MLB team and season."""
        pass

    