from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from entities.players import PlayerSearchResult, PlayerDetail, SeasonStats
from config.firebase import firebase_service
from typing import List, Dict

class PlayerDomain:
    """Contains the business logic related to players"""
    def __init__(self):
        pass
    
    def validate_search_query(self, query: str) -> None:
        """Vallidate search query"""
        if not query or query.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query is required"
            )


    def _get_player_image_url(self, player_id: int) -> str:
        """Generate MLB player headshot URL"""
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
    
    def fuzzy_search(self,players: List[Dict], query: str, limit: int = 5, score_cutoff: int = 60) -> List[PlayerSearchResult]:
        """
        Search for players by name using fuzzy matching
        This is a public search - no authentication required.
        """
        q = (query or "").strip()
        if not q:
            return []

        player_names = [p.get("name", "") for p in players]
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
        for _name, score, idx in matches:
            player = players[idx]
            mlbam_id = player.get("mlbam_id")
            seasons = player.get("seasons", {})
            
            if not isinstance(mlbam_id, int) or mlbam_id <= 0:
                continue
            results.append(PlayerSearchResult(
                id=mlbam_id,
                name=player.get("name", ""),
                score=score,
                image_url=self._get_player_image_url(mlbam_id),
                years_active=self._get_years_active(seasons)
            ))
        
        return results
    
    def build_player_detail(self, player_data: Dict) -> PlayerDetail:
        """
        Get and return a detailed information for a specific player including all seasons stats.
        Returns the full player with all  advanced stats.
        """
        if not player_data:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

        seasons_dict = {}
        for year, stats in player_data.get("seasons", {}).items():
            # Handle 'def' field (Python keyword)
            if "def" in stats:
                stats["def_"] = stats.pop("def")
            seasons_dict[year] = SeasonStats(**stats)
        
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

    def validate_player_id(self, player_id: int) -> None:
        """Validate player ID"""
        if not player_id or player_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid player ID")
        

