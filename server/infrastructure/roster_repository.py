from repositories.roster_avg_repository import RosterRepository
from typing import Dict, Optional, List
from fastapi import HTTPException, status
from anyio import to_thread
import logging

class RosterRepositoryFirebase(RosterRepository):
    def __init__(self, db):
        self.db = db 
        self._logger = logging.getLogger(__name__)
    
    def _get_player_seasons_blocking(self, player_id: int) -> Optional[Dict]:
        """Blocking version: Get seasons data for a single player"""
        player_doc = self.db.collection('players').document(str(player_id)).get()
        
        if not player_doc.exists:
            return None
        
        player_data = player_doc.to_dict()
        seasons = player_data.get("seasons", {})
        
        return seasons if seasons else None
    
    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """Gets a dictionary of mlb ids with a dictionary of there seasons stats"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
    
        try:
            players_data: Dict[int, Dict] = {}
            for player_id in player_ids:
                seasons = await to_thread.run_sync(self._get_player_seasons_blocking, player_id)
                if seasons is not None:
                    players_data[player_id] = seasons
            
            return players_data
        except Exception as e:
            self._logger.exception("Failed to calculate roster averages")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate roster averages"
            ) from e