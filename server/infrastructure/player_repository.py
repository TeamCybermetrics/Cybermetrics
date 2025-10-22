from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from models.players import PlayerSearchResult, PlayerDetail, SeasonStats
from config.firebase import firebase_service
from typing import List, Dict, Optional
from repositories.player_repository import PlayerRepository

class PlayerRepositoryFirebase(PlayerRepository):
    def __init__(self, db = None):
        self.db = db or firebase_service.db
        self._players_cache: List[Dict] = []
        self._cache_loaded = False
    
    def _load_database(self):
        """Load all players from Firebase into memory for fast searching"""
        if not self._cache_loaded and self.db:
            try:
                players_ref = self.db.collection('players').stream()
                self._players_cache = [doc.to_dict() for doc in players_ref]
                self._cache_loaded = True
                print(f"Loaded {len(self._players_cache)} players from Firebase")
            except Exception as e:
                print(f"Error loading players cache: {e}")
    
    async def get_all_players(self) -> List[Dict]:
        """
        Get all players from user searchbar using the in memory search
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        self._load_database()
        return self._players_cache
        
    
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Gets a specific player from database through mlb id"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        try:
            player_document = self.db.collection('players').document(str(player_id)).get()
            if not player_document.exists:
                return None
            return player_document.to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get player: {str(e)}"
            )

