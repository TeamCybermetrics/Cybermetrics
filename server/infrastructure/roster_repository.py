from repositories.roster_avg_repository import RosterRepository
from typing import Dict, Optional, List
from fastapi import HTTPException, status

class RosterRepositoryFirebase(RosterRepository):
    def __init__(self, db):
        self.db = db 
    
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
                player_doc = self.db.collection('players').document(str(player_id)).get()
                
                if not player_doc.exists:
                    continue
                
                player_data = player_doc.to_dict()
                seasons = player_data.get("seasons", {})
                
                if not seasons:
                    continue
                players_data[player_id] = seasons
                
            return players_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate roster averages: {str(e)}"
            )