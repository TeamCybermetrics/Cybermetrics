from fastapi import HTTPException, status
from models.players import RosterAvgResponse, PlayerAvgStats
from typing import List, Dict
from repositories.roster_avg_repository import RosterRepository
from domain.roster_domain import RosterDomain

class RosterAvgService:
    """Service for calculating roster average statistics"""
    
    def __init__(self, roster_repository: RosterRepository, roster_domain: RosterDomain):
        self.roster_repository = roster_repository
        self.roster_domain = roster_domain
    
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
        self.roster_domain.validate_player_ids(player_ids)

        players_data = await self.roster_repository.get_players_seasons_data(player_ids)

        averages = self.roster_domain.calculate_roster_averages(players_data)

        return averages



