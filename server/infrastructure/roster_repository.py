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

    def _get_league_unweighted_blocking(self) -> Dict[str, float]:
        """Blocking fetch for league unweighted averages from Firestore."""
        doc = self.db.collection("league").document("averages").get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League averages document not found",
            )
        data = doc.to_dict() or {}
        unweighted = data.get("unweighted")
        if not isinstance(unweighted, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="League unweighted averages missing or malformed",
            )
        # Ensure values are floats
        return {k: float(v) for k, v in unweighted.items() if isinstance(v, (int, float))}

    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """Fetch league unweighted averages (async wrapper)."""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )
        try:
            return await to_thread.run_sync(self._get_league_unweighted_blocking)
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to fetch league unweighted averages")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch league averages",
            ) from e