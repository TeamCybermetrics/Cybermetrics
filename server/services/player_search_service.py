from pybaseball import chadwick_register
from rapidfuzz import process, fuzz
from fastapi import HTTPException, status
from models.players import PlayerSearchResult, PlayerDetail
from typing import List, Optional

class PlayerSearchService:
    """Service for searching baseball players using pybaseball database"""
    def __init__(self):
        self.df = None
        self._names: list[str] = []
        self._names_lower: list[str] = []
    
    def _load_database(self):
        """Load the player database from pybaseball"""
        if self.df is None:
            df = chadwick_register()[
                ["key_mlbam", "name_first", "name_last", "mlb_played_first", "mlb_played_last",
                 "key_retro", "key_bbref", "key_fangraphs"]
            ].fillna("")
            df["full_name"] = (df["name_first"].astype(str) + " " + df["name_last"].astype(str)).str.strip()
            self.df = df
            self._names = df["full_name"].tolist()
            self._names_lower = [n.lower() for n in self._names]
    
    def _get_player_image_url(self, player_id: int) -> str:
        """Generate MLB player headshot URL"""
        # MLB's official headshot URL - falls back to generic if player not found
        return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{player_id}/headshot/67/current"
    
    def _get_years_active(self, row) -> str:
        """Get years active string"""
        first_year = str(row["mlb_played_first"]) if row["mlb_played_first"] else ""
        last_year = str(row["mlb_played_last"]) if row["mlb_played_last"] else ""
        
        if first_year and last_year:
            if first_year == last_year:
                return first_year
            return f"{first_year}-{last_year}"
        elif first_year:
            return f"{first_year}-Present"
        return "Unknown"
    
    async def search(self, query: str, limit: int = 5, score_cutoff: int = 70) -> List[PlayerSearchResult]:
        """
        Search for players by name using fuzzy matching.
        This is a public search - no authentication required.
        """
        self._load_database()
        q = (query or "").strip()
        if not q:
            return []
        
        q_lower = q.lower()
        matches = process.extract(
            q_lower,
            self._names_lower,
            limit=limit,
            scorer=fuzz.WRatio,
            score_cutoff=score_cutoff,
        )

        results = []
        for name, score, idx in matches:
            row = self.df.iloc[idx]
            player_id = int(row["key_mlbam"])
            
            results.append(PlayerSearchResult(
                id=player_id,
                name=self._names[idx],
                score=score,
                image_url=self._get_player_image_url(player_id),
                years_active=self._get_years_active(row)
            ))
        
        return results
    
    async def get_player_detail(self, player_id: int) -> PlayerDetail:
        """Get detailed information for a specific player"""
        self._load_database()
        
        # Find player by ID
        player_row = self.df[self.df["key_mlbam"] == player_id]
        
        if player_row.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
        
        row = player_row.iloc[0]
        
        # Safely extract all available data, handling various null/empty cases
        def safe_str(value):
            """Safely convert value to string if it exists and is not empty"""
            if value is None or value == "" or (isinstance(value, float) and value != value):  # NaN check
                return None
            try:
                return str(int(value)) if isinstance(value, float) else str(value)
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            """Safely convert value to int if it exists and is not empty"""
            if value is None or value == "" or (isinstance(value, float) and value != value):  # NaN check
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        return PlayerDetail(
            id=player_id,
            name=f"{row['name_first']} {row['name_last']}".strip(),
            image_url=self._get_player_image_url(player_id),
            years_active=self._get_years_active(row),
            first_name=safe_str(row["name_first"]) or "",
            last_name=safe_str(row["name_last"]) or "",
            mlb_played_first=safe_str(row["mlb_played_first"]),
            mlb_played_last=safe_str(row["mlb_played_last"]),
            key_retro=safe_str(row["key_retro"]),
            key_bbref=safe_str(row["key_bbref"]),
            key_fangraphs=safe_int(row["key_fangraphs"])
        )


# Singleton instance
player_search_service = PlayerSearchService()
