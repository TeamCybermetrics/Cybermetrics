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
    

