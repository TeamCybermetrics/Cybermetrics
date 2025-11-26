from repositories.player_repository import PlayerRepository
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, Mock
from repositories.roster_avg_repository import RosterRepository

class MockRosterRepository(RosterRepository):
    """Mock implementation of RosterRepository for testing"""
    
    def __init__(self):
        self._players_seasons_data: Dict[int, Dict] = {}
        self._league_avg: Dict[str, float] = {}
        self._league_std: Dict[str, float] = {}
    
    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """Get seasons data for multiple players."""
        result = {}
        for pid in player_ids:
            if pid in self._players_seasons_data:
                result[pid] = self._players_seasons_data[pid]
        return result
    
    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """Fetch league-wide unweighted average stats."""
        return self._league_avg.copy()
    
    async def get_league_unweighted_std(self) -> Dict[str, float]:
        """Fetch league-wide unweighted standard deviations."""
        return self._league_std.copy()
    
    async def get_league_weighted_std(self) -> Dict[str, float]:
        pass
    
    def fetch_team_roster(self, team_id: int, season: int) -> Dict[str, any]:
        pass

    # Helper methods for test setup and edge case creation for use case interactor unit testing
    def set_players_seasons_data(self, player_id: int, seasons: Dict):
        """Set season data for a player."""
        self._players_seasons_data[player_id] = seasons
    
    def set_league_avg(self, league_avg: Dict[str, float]):
        """Set league average stats."""
        self._league_avg = league_avg.copy()
    
    def set_league_std(self, league_std: Dict[str, float]):
        """Set league standard deviations."""
        self._league_std = league_std.copy()

class MockPlayerRepository(PlayerRepository):
    """Mock implementation of PlayerRepository for testing."""
    
    def __init__(self):
        self._players: List[Dict] = []
        self._player_by_id: Dict[int, Dict] = {}
    
    async def get_all_players(self) -> List[Dict]:
        """Get all players from database."""
        return self._players.copy()
    
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get a specific player by ID."""
        return self._player_by_id.get(player_id)
    
    def upload_team(self, team, team_name, final_players):
        pass
    
    def bulk_upsert_players(self, players: List[Dict[str, any]]) -> None:
        pass
    
    def set_league_averages(self, league_doc: Dict[str, any]) -> None:
        pass
    def build_player_image_url(self, player_id: int) -> str:
        """Return a player headshot URL."""
        return f"https://example.com/players/{player_id}.jpg"
    
    # heelper methods for test setup to add to in memory database 
    def add_player(self, player: Dict):
        """Add a player to the mock repository."""
        mlbam_id = player.get("mlbam_id")
        if mlbam_id:
            self._player_by_id[mlbam_id] = player
        self._players.append(player)
    
    def set_player(self, player_id: int, player: Dict):
        """Set a specific player by ID."""
        self._player_by_id[player_id] = player

