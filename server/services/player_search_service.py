from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from models.players import PlayerSearchResult, PlayerDetail, SeasonStats
from config.firebase import firebase_service
from typing import List, Dict

class PlayerSearchService:
    """Service for searching baseball players from Firebase database"""
    def __init__(self):
        self.db = firebase_service.db
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
    
    def _get_player_image_url(self, player_id: int) -> str:
        """Generate MLB player headshot URL"""
        # MLB's official headshot URL - falls back to generic if player not found
        return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{player_id}/headshot/67/current"
    
    def _get_years_active(self, seasons: Dict) -> str:
        """Get years active string from seasons data"""
        if not seasons:
            return "Unknown"
        
        years = sorted([int(year) for year in seasons.keys()])
        if not years:
            return "Unknown"
        
        first_year = str(years[0])
        last_year = str(years[-1])
        
        if first_year == last_year:
            return first_year
        return f"{first_year}-{last_year}"
    
    async def search(self, query: str, limit: int = 5, score_cutoff: int = 60) -> List[PlayerSearchResult]:
        """
        Search for players by name using fuzzy matching from Firebase.
        This is a public search - no authentication required.
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        self._load_database()
        
        q = (query or "").strip()
        if not q:
            return []
        
        # Extract player names for fuzzy matching
        player_names = [p.get("name", "") for p in self._players_cache]
        player_names_lower = [n.lower() for n in player_names]
        
        q_lower = q.lower()
        matches = process.extract(
            q_lower,
            player_names_lower,
            limit=limit,
            scorer=fuzz.WRatio,
            score_cutoff=score_cutoff,
        )

        results = []
        for name, score, idx in matches:
            player = self._players_cache[idx]
            mlbam_id = player.get("mlbam_id")
            seasons = player.get("seasons", {})
            
            results.append(PlayerSearchResult(
                id=mlbam_id,
                name=player.get("name", ""),
                score=score,
                image_url=self._get_player_image_url(mlbam_id),
                years_active=self._get_years_active(seasons)
            ))
        
        return results
    
    async def get_player_detail(self, player_id: int) -> PlayerDetail:
        """
        Get detailed information for a specific player including all seasons stats.
        Returns the full player document from Firebase with all advanced stats.
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            player_doc = self.db.collection('players').document(str(player_id)).get()
            
            if not player_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with ID {player_id} not found"
                )
            
            player_data = player_doc.to_dict()
            
            # Convert seasons dict to SeasonStats objects
            seasons_dict = {}
            for year, stats in player_data.get("seasons", {}).items():
                # Handle 'def' field (Python keyword)
                if "def" in stats:
                    stats["def_"] = stats.pop("def")
                seasons_dict[year] = SeasonStats(**stats)
            
            # Build PlayerDetail response
            return PlayerDetail(
                mlbam_id=player_data.get("mlbam_id"),
                fangraphs_id=player_data.get("fangraphs_id"),
                name=player_data.get("name", ""),
                image_url=self._get_player_image_url(player_data.get("mlbam_id")),
                years_active=self._get_years_active(player_data.get("seasons", {})),
                team_abbrev=player_data.get("team_abbrev"),
                overall_score=player_data.get("overall_score", 0.0),
                seasons=seasons_dict
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get player details: {str(e)}"
            )


# Singleton instance
player_search_service = PlayerSearchService()
