from rapidfuzz import process, fuzz
from dtos.player_dtos import PlayerSearchResult, PlayerDetail
from entities.players import SeasonStats
from typing import List, Dict
from repositories.player_repository import PlayerRepository
from useCaseHelpers.player_helper import PlayerDomain

class PlayerSearchService:
    """Service for searching baseball players from Firebase database"""
    def __init__(self, player_repository: PlayerRepository, player_domain: PlayerDomain):
        self.player_repository = player_repository
        self.player_domain = player_domain
    
    
    async def search(self, query: str, limit: int = 5, score_cutoff: int = 60) -> List[PlayerSearchResult]:
        """
        Search for players by name using fuzzy matching 
        This is a public search - no authentication required.
        """
        self.player_domain.validate_search_query(query)

        searched_players = await self.player_repository.get_all_players()

        return self.player_domain.fuzzy_search(
            searched_players,
            query,
            limit,
            score_cutoff,
            self.player_repository.build_player_image_url,
        )
    
    async def get_player_detail(self, player_id: int) -> PlayerDetail:
        """
        Get detailed information for a specific player including all seasons stats.
        Returns the full player document from Firebase with all advanced stats.
        """
        self.player_domain.validate_player_id(player_id)
        
        player_data = await self.player_repository.get_player_by_id(player_id)
        
        return self.player_domain.build_player_detail(
            player_data,
            self.player_repository.build_player_image_url,
        )

