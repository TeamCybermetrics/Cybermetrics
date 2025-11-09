from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from models.players import PlayerSearchResult, PlayerDetail, SeasonStats
from config.firebase import firebase_service
from typing import List, Dict, Optional
from repositories.player_repository import PlayerRepository
from anyio import to_thread, Lock
import logging

class PlayerRepositoryFirebase(PlayerRepository):
    def __init__(self, db):
        self.db = db 
        self._players_cache: List[Dict] = []
        self._players_cache_by_id: Dict[int, Dict] = {}
        self._cache_loaded = False
        self._logger = logging.getLogger(__name__)
        self._load_lock = Lock()
    
    def _load_database_blocking(self) -> int:
        """Blocking version: Load all players from Firebase into memory"""
        players_ref = self.db.collection('players').stream()
        cache: List[Dict] = []
        cache_by_id: Dict[int, Dict] = {}
        for doc in players_ref:
            data = doc.to_dict()
            cache.append(data)
            try:
                mlbam_id = int(data.get("mlbam_id"))
            except (TypeError, ValueError):
                continue
            cache_by_id[mlbam_id] = data
        self._players_cache = cache
        self._players_cache_by_id = cache_by_id
        self._cache_loaded = True
        return len(self._players_cache)
    
    async def _ensure_cache_loaded(self) -> None:
        """Ensure the player cache is loaded (non-blocking)"""
        if self._cache_loaded:
            return
        if not self.db:
            return
        
        # lock to prevent concurrent loads
        async with self._load_lock:
            # double check after acquiring lock as antoher request may have been loaded
            if self._cache_loaded:
                return
            
            try:
                count = await to_thread.run_sync(self._load_database_blocking)
                self._logger.info("Loaded %d players from Firebase", count)
            except Exception as e:
                self._logger.exception("Error loading players cache")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to load players cache"
                ) from e
    
    async def get_all_players(self) -> List[Dict]:
        """
        Get all players from user searchbar using the in memory search
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        await self._ensure_cache_loaded()
        return self._players_cache
        
    
    def _get_player_by_id_blocking(self, player_id: int) -> Optional[Dict]:
        """Blocking version: Get specific player from database"""
        player_document = self.db.collection('players').document(str(player_id)).get()
        if not player_document.exists:
            return None
        return player_document.to_dict()
    
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Gets a specific player from database through mlb id"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        await self._ensure_cache_loaded()

        cached = self._players_cache_by_id.get(player_id)
        if cached is not None:
            return cached

        try:
            player_data = await to_thread.run_sync(self._get_player_by_id_blocking, player_id)
            if player_data:
                self._players_cache_by_id[player_id] = player_data
                self._players_cache.append(player_data)
            return player_data
        except Exception as e:
            self._logger.exception("Failed to get player by id: %s", player_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get player"
            ) from e

