from repositories.roster_avg_repository import RosterRepository
from typing import Dict, Optional, List, Any
from fastapi import HTTPException, status
from anyio import to_thread, Lock
import logging
import requests

class RosterRepositoryFirebase(RosterRepository):
    def __init__(self, db):
        self.db = db 
        self._logger = logging.getLogger(__name__)
        self._free_agents_cache: List[Dict[str, Any]] = []
        self._free_agents_loaded = False
        self._free_agents_lock = Lock()
    
    def _get_player_seasons_blocking(self, player_id: int) -> Optional[Dict]:
        """Blocking version: Get seasons data for a single player"""
        player_doc = self.db.collection('players').document(str(player_id)).get()
        
        if not player_doc.exists:
            return None
        
        player_data = player_doc.to_dict()
        seasons = player_data.get("seasons", {})
        
        return seasons if seasons else None
    
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
                seasons = await to_thread.run_sync(self._get_player_seasons_blocking, player_id)
                if seasons is not None:
                    players_data[player_id] = seasons
            
            return players_data
        except Exception as e:
            self._logger.exception("Failed to calculate roster averages")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate roster averages"
            ) from e

    def _get_league_unweighted_blocking(self) -> Dict[str, float]:
        """Blocking fetch for league unweighted averages from Firestore."""
        doc = self.db.collection("league").document("averages").get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League averages document not found",
            )
        data = doc.to_dict() or {}
        unweighted = data.get("unweighted")
        if not isinstance(unweighted, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="League unweighted averages missing or malformed",
            )
        
        required = {"strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running"}
        result: Dict[str, float] = {}
        missing_or_bad = []
        for k in required:
            v = unweighted.get(k)
            try:
                result[k] = float(v)
            except(TypeError, ValueError):
                missing_or_bad.append(k)
        if missing_or_bad:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"League unweighted averages missing or non-numeric for: {', '.join(missing_or_bad)}",
            )
        return result

    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """Fetch league unweighted averages (async wrapper)."""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )
        try:
            return await to_thread.run_sync(self._get_league_unweighted_blocking)
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to fetch league unweighted averages")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch league averages",
            ) from e

    def _get_league_unweighted_std_blocking(self) -> Dict[str, float]:
        """Blocking fetch for league unweighted standard deviations from Firestore."""
        doc = self.db.collection("league").document("averages").get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League averages document not found",
            )
        data = doc.to_dict() or {}
        std_map = data.get("unweighted_std")
        if not isinstance(std_map, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="League unweighted std devs missing or malformed",
            )
        required = {"strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running"}
        result: Dict[str, float] = {}
        missing_or_bad = []
        for k in required:
            v = std_map.get(k)
            try:
                result[k] = float(v)
            except (TypeError, ValueError):
                missing_or_bad.append(k)
        if missing_or_bad:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"League unweighted std devs missing or non-numeric for: {', '.join(missing_or_bad)}",
            )
        return result

    async def get_league_unweighted_std(self) -> Dict[str, float]:
        """Fetch league unweighted standard deviations (async wrapper)."""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )
        try:
            return await to_thread.run_sync(self._get_league_unweighted_std_blocking)
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to fetch league unweighted std deviations")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch league std deviations",
            ) from e

    def _get_league_weighted_std_blocking(self) -> Dict[str, float]:
        """Blocking fetch for league weighted-by-player-count std deviations from Firestore."""
        doc = self.db.collection("league").document("averages").get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League averages document not found",
            )
        data = doc.to_dict() or {}
        std_map = data.get("weighted_by_player_count_std")
        if not isinstance(std_map, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="League weighted std devs missing or malformed",
            )
        required = {"strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running"}
        result: Dict[str, float] = {}
        missing_or_bad = []
        for k in required:
            v = std_map.get(k)
            try:
                result[k] = float(v)
            except (TypeError, ValueError):
                missing_or_bad.append(k)
        if missing_or_bad:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"League weighted std devs missing or non-numeric for: {', '.join(missing_or_bad)}",
            )
        return result

    async def get_league_weighted_std(self) -> Dict[str, float]:
        """Fetch league weighted-by-player-count standard deviations (async wrapper)."""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )
        try:
            return await to_thread.run_sync(self._get_league_weighted_std_blocking)
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Failed to fetch league weighted std deviations")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch league std deviations",
            ) from e

    def fetch_team_roster(self, team_id: int, season: int) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/Active",
                params={"season": season},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            self._logger.warning(
                "Failed to fetch active roster for team %s in season %s: %s",
                team_id,
                season,
                exc,
            )
            return {}

    