from rapidfuzz import process, fuzz
from entities.players import PlayerSearchResult, PlayerDetail, SeasonStats
from typing import List, Dict, Optional, Callable
from .errors import InputValidationError, QueryError


class PlayerDomain:
    """Contains the business logic related to players"""
    def __init__(self):
        pass
    
    def validate_search_query(self, query: str) -> None:
        """Vallidate search query"""
        if not query or query.strip() == "":
            raise InputValidationError("Search query is required")


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
    
    def _build_player_search_result(
        self,
        player: Dict,
        score: float,
        image_builder: Optional[Callable[[int], str]] = None,
    ) -> Optional[PlayerSearchResult]:
        """Construct a PlayerSearchResult from raw player data."""
        mlbam_id = player.get("mlbam_id")
        seasons = player.get("seasons", {})

        if not isinstance(mlbam_id, int) or mlbam_id <= 0:
            return None

        builder = image_builder or (lambda _: "")

        return PlayerSearchResult(
            id=mlbam_id,
            name=player.get("name", ""),
            score=score,
            image_url=builder(mlbam_id),
            years_active=self._get_years_active(seasons),
        )
    
    def build_player_search_result(
        self,
        player: Dict,
        score: float,
        image_builder: Optional[Callable[[int], str]] = None,
    ) -> Optional[PlayerSearchResult]:
        """Public helper to construct a player search result."""
        return self._build_player_search_result(player, score, image_builder)
    
    def fuzzy_search(
        self,
        players: List[Dict],
        query: str,
        limit: int = 5,
        score_cutoff: int = 60,
        image_builder: Optional[Callable[[int], str]] = None,
    ) -> List[PlayerSearchResult]:
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
            search_result = self._build_player_search_result(player, score, image_builder)
            if search_result:
                results.append(search_result)
        
        return results
    
    def build_player_detail(
        self,
        player_data: Dict,
        image_builder: Optional[Callable[[int], str]] = None,
    ) -> PlayerDetail:
        """
        Get and return a detailed information for a specific player including all seasons stats.
        Returns the full player with all  advanced stats.
        """
        if not player_data:
            raise QueryError("Player not found")

        seasons_dict = {}
        for year, stats in player_data.get("seasons", {}).items():
            # Handle 'def' field (Python keyword)
            if "def" in stats:
                stats["def_"] = stats.pop("def")
            seasons_dict[year] = SeasonStats(**stats)
        
        mlbam_id = player_data.get("mlbam_id")

        return PlayerDetail(
            mlbam_id=mlbam_id,
            fangraphs_id=player_data.get("fangraphs_id"),
            name=player_data.get("name", ""),
            image_url=(image_builder or (lambda _: ""))(mlbam_id),
            years_active=self._get_years_active(player_data.get("seasons", {})),
            team_abbrev=player_data.get("team_abbrev"),
            overall_score=player_data.get("overall_score", 0.0),
            seasons=seasons_dict
        )

    def validate_player_id(self, player_id: int) -> None:
        """Validate player ID"""
        if not player_id or player_id <= 0:
            raise InputValidationError("Invalid player ID")
    
    def get_primary_position(
        self, player_data: Dict, seasons: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Derive a player's primary defensive position.

        Checks, in order:
          1. Explicit `position` field on the player document.
          2. `positions` field on the document (list of abbreviations or dicts).
          3. Latest season data for `primary_position`, `position`, or `positions`.
        """
        def normalize(pos: Optional[str]) -> Optional[str]:
            if isinstance(pos, str):
                cleaned = pos.strip().upper()
                return cleaned or None
            return None

        position_value = normalize(player_data.get("position"))
        if position_value:
            return position_value

        positions_field = player_data.get("positions")
        if isinstance(positions_field, list) and positions_field:
            first = positions_field[0]
            if isinstance(first, dict):
                return normalize(first.get("abbreviation") or first.get("code"))
            return normalize(first)

        seasons_data = seasons if seasons is not None else player_data.get("seasons")
        if isinstance(seasons_data, dict) and seasons_data:
            try:
                ordered_years = sorted((int(y) for y in seasons_data.keys()), reverse=True)
            except Exception:
                ordered_years = list(seasons_data.keys())[::-1]

            for year in ordered_years:
                key = str(year)
                stats = seasons_data.get(key) or {}
                if not isinstance(stats, dict):
                    continue
                pos = normalize(stats.get("primary_position") or stats.get("position"))
                if pos:
                    return pos

                positions_list = stats.get("positions")
                if isinstance(positions_list, list) and positions_list:
                    first_pos = positions_list[0]
                    if isinstance(first_pos, dict):
                        pos = normalize(first_pos.get("abbreviation") or first_pos.get("code"))
                    else:
                        pos = normalize(first_pos)
                    if pos:
                        return pos

        return None


