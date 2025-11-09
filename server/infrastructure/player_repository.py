from datetime import datetime
from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from entities.players import PlayerSearchResult, PlayerDetail, SeasonStats
from config.firebase import firebase_service
from typing import List, Dict, Optional, Any
from repositories.player_repository import PlayerRepository
from anyio import to_thread, Lock
import logging

class PlayerRepositoryFirebase(PlayerRepository):
    def __init__(self, db):
        self.db = db 
        self._players_cache: List[Dict] = []
        self._cache_loaded = False
        self._logger = logging.getLogger(__name__)
        self._load_lock = Lock()
    
    def _load_database_blocking(self) -> int:
        """Blocking version: Load all players from Firebase into memory"""
        players_ref = self.db.collection('players').stream()
        self._players_cache = [doc.to_dict() for doc in players_ref]
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
        try:
            player_data = await to_thread.run_sync(self._get_player_by_id_blocking, player_id)
            return player_data
        except Exception as e:
            self._logger.exception("Failed to get player by id: %s", player_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get player"
            ) from e

    def upload_team(self, team, team_name, final_players) -> None:
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )

        if final_players != []:
            self.db.collection("teams").document(team.upper()).set({
                "full_team_name": team_name,
                "positional_players": final_players,
                "number": len(final_players)
            }, merge=True)
        else:
            return
        
    def bulk_upsert_players(self, players: List[Dict[str, Any]]) -> None:
        if not players:
            return
        batch = self.db.batch()
        col = self.db.collection("players")
        for p in players:
            doc = col.document(str(p["mlbam_id"]))
            batch.set(doc, p, merge=True)
        batch.commit()

    def list_team_ids(self) -> List[str]:
        if not self.db:
            return []
        try:
            return [doc.id for doc in self.db.collection("teams").list_documents()]
        except Exception:
            self._logger.exception("list_team_ids failed")
            return []

    def get_team_positional_players(self, team_id: str) -> List[Dict]:
        if not self.db:
            return []
        try:
            snap = self.db.collection("teams").document(team_id.upper()).get()
            if not snap.exists:
                return []
            data = snap.to_dict() or {}
            return data.get("positional_players", []) or []
        except Exception:
            self._logger.exception("get_team_positional_players failed for %s", team_id)
            return []

    def set_team_roster_average(self, team_id: str, avg: Dict[str, float]) -> None:
        if not self.db:
            return
        try:
            self.db.collection("teams").document(team_id.upper()).set(
                {
                    "roster_average": avg,
                    "roster_average_updated_at": datetime.utcnow().isoformat() + "Z",
                },
                merge=True,
            )
        except Exception:
            self._logger.exception("set_team_roster_average failed for %s", team_id)

    def set_league_averages(self, league_doc: Dict[str, Any]) -> None:
        if not self.db:
            return
        try:
            self.db.collection("league").document("averages").set(league_doc, merge=True)
        except Exception:
            self._logger.exception("set_league_averages failed")