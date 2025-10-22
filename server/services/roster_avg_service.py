from fastapi import HTTPException, status
from config.firebase import firebase_service
from models.players import RosterAvgResponse, PlayerAvgStats
from typing import List, Dict

class RosterAvgService:
    """Service for calculating roster average statistics"""
    
    def __init__(self):
        self.db = firebase_service.db
    
    async def get_roster_averages(self, player_ids: List[int]) -> RosterAvgResponse:
        """
        Get average stats for a list of player IDs.
        
        Calculates career averages across all seasons for:
        - Strikeout rate (K%)
        - Walk rate (BB%)
        - Isolated power (ISO)
        - On-base percentage (OBP)
        - Base running value (BsR)
        
        Args:
            player_ids: List of MLB player IDs (mlbam_id)
            
        Returns:
            RosterAvgResponse with stats for each player
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        if not player_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player IDs list cannot be empty"
            )
        
        try:
            stats_dict: Dict[int, PlayerAvgStats] = {}
            
            for player_id in player_ids:
                player_doc = self.db.collection('players').document(str(player_id)).get()
                
                if not player_doc.exists:
                    # Skip players not found, or optionally raise error
                    continue
                
                player_data = player_doc.to_dict()
                seasons = player_data.get("seasons", {})
                
                if not seasons:
                    # No season data, skip this player
                    continue
                
                # Calculate career averages across all seasons
                total_strikeout_rate = 0.0
                total_walk_rate = 0.0
                total_isolated_power = 0.0
                total_on_base_percentage = 0.0
                total_base_running = 0.0
                season_count = 0
                
                for year, stats in seasons.items():
                    # Only count seasons with plate appearances
                    if stats.get("plate_appearances", 0) > 0:
                        total_strikeout_rate += stats.get("strikeout_rate", 0.0)
                        total_walk_rate += stats.get("walk_rate", 0.0)
                        total_isolated_power += stats.get("isolated_power", 0.0)
                        total_on_base_percentage += stats.get("on_base_percentage", 0.0)
                        total_base_running += stats.get("base_running", 0.0)
                        season_count += 1
                
                if season_count > 0:
                    # Calculate averages
                    avg_strikeout_rate = round(total_strikeout_rate / season_count, 3)
                    avg_walk_rate = round(total_walk_rate / season_count, 3)
                    avg_isolated_power = round(total_isolated_power / season_count, 3)
                    avg_on_base_percentage = round(total_on_base_percentage / season_count, 3)
                    avg_base_running = round(total_base_running / season_count, 3)
                    
                    stats_dict[player_id] = PlayerAvgStats(
                        strikeout_rate=avg_strikeout_rate,
                        walk_rate=avg_walk_rate,
                        isolated_power=avg_isolated_power,
                        on_base_percentage=avg_on_base_percentage,
                        base_running=avg_base_running
                    )
            
            return RosterAvgResponse(
                stats=stats_dict,
                total_players=len(stats_dict)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate roster averages: {str(e)}"
            )


# Singleton instance
roster_avg_service = RosterAvgService()
