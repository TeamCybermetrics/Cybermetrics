from fastapi import HTTPException, status
from models.players import PlayerAvgStats, RosterAvgResponse
from typing import Dict, List, Optional

class RosterDomain:
    def __init__(self):
        pass

    def validate_player_ids(self, player_ids: List[int]) -> None:
        """Validate player IDs input"""
        if not player_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player IDs list cannot be empty"
            )
    
    def calculate_player_averages(self, seasons: Dict) -> Optional[PlayerAvgStats]:
        """Calculate career averages for a single player"""
        if not seasons:
            return None
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
            avg_strikeout_rate = round(total_strikeout_rate / season_count, 3)
            avg_walk_rate = round(total_walk_rate / season_count, 3)
            avg_isolated_power = round(total_isolated_power / season_count, 3)
            avg_on_base_percentage = round(total_on_base_percentage / season_count, 3)
            avg_base_running = round(total_base_running / season_count, 3)
            
            return PlayerAvgStats(
                strikeout_rate=avg_strikeout_rate,
                walk_rate=avg_walk_rate,
                isolated_power=avg_isolated_power,
                on_base_percentage=avg_on_base_percentage,
                base_running=avg_base_running
            )
        
        return None
    
    def calculate_roster_averages(self, players_data: Dict[int, Dict]) -> RosterAvgResponse:
        """Calculate averages for entire roster"""
        stats_dict: Dict[int, PlayerAvgStats] = {}
        for player_id, season_stats in players_data.items():
            player_averages = self.calculate_player_averages(season_stats)
            if player_averages is not None:
                stats_dict[player_id] = player_averages
        return RosterAvgResponse(
            stats=stats_dict,
            total_players=len(stats_dict)
        )