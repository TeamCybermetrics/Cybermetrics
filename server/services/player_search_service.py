from pybaseball import chadwick_register
from rapidfuzz import process, fuzz
from models.players import PlayerSearchResult
from typing import List

class PlayerSearchService:
    """Service for searching baseball players using pybaseball database"""
    def __init__(self):
        self.df = None
        self._names: list[str] = []
        self._names_lower: list[str] = []
    
    def _load_database(self):
        """Load the player database from pybaseball"""
        if self.df is None:
            df = chadwick_register()[["key_mlbam", "name_first", "name_last"]].fillna("")
            df["full_name"] = (df["name_first"].astype(str) + " " + df["name_last"].astype(str)).str.strip()
            self.df = df
            self._names = df["full_name"].tolist()
            self._names_lower = [n.lower() for n in self._names]
    
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

        return [
            PlayerSearchResult(
                id=int(self.df.iloc[idx]["key_mlbam"]),
                name=self._names[idx],
                score=score,
            )
            for name, score, idx in matches
        ]


# Singleton instance
player_search_service = PlayerSearchService()
