from repositories.player_repository import PlayerRepository
from typing import Dict, List, Optional, Any
from unittest.mock import AsyncMock, Mock
from repositories.roster_avg_repository import RosterRepository


class MockRosterRepository(RosterRepository):
    """Mock implementation of RosterRepository for testing with dynamic fallback."""

    def __init__(self):
        """
        Initialize the mock repository with empty in-memory storage for player seasonal data and league statistics.
        
        Attributes:
            _players_seasons_data (Dict[int, Dict]): Mapping from player ID to their seasons dictionary.
            _league_avg (Dict[str, float]): League unweighted average statistics (empty until set or computed).
            _league_std (Dict[str, float]): League unweighted standard-deviation statistics (empty until set or computed).
        """
        self._players_seasons_data: Dict[int, Dict] = {}
        self._league_avg: Dict[str, float] = {}
        self._league_std: Dict[str, float] = {}

    async def get_players_seasons_data(self, player_ids: List[int]) -> Dict[int, Dict]:
        """
        Retrieve stored seasonal data for the given player IDs.
        
        Parameters:
            player_ids (List[int]): Player IDs to look up. Only players present in the repository are included in the result.
        
        Returns:
            Dict[int, Dict]: Mapping from player ID to that player's seasons data for each player found.
        """
        result = {}
        for pid in player_ids:
            if pid in self._players_seasons_data:
                result[pid] = self._players_seasons_data[pid]
        return result

    async def get_league_unweighted_average(self) -> Dict[str, float]:
        """
        Return the league unweighted average stat vector.
        
        If a stored league-average vector exists, return a shallow copy of it; otherwise compute the average across the latest available seasonal snapshot for each player. The returned dictionary contains the per-stat averages for the keys: `strikeout_rate`, `walk_rate`, `isolated_power`, `on_base_percentage`, and `base_running`.
        
        Returns:
            Dict[str, float]: Mapping from stat name to average value (floats). Empty or missing player data yields zeros for each stat.
        """
        if self._league_avg:
            return self._league_avg.copy()
        snapshots = [self._extract_latest_stats(s) for s in self._players_seasons_data.values() if s]
        snapshots = [s for s in snapshots if s]
        return self._average_dicts(snapshots)

    async def get_league_unweighted_std(self) -> Dict[str, float]:
        """
        Compute the league standard deviation for tracked batting statistics.
        
        If an explicit league std has been set, a shallow copy of it is returned; otherwise the standard deviation is computed across each player's latest available season snapshot. Returns zero for each tracked key when there is no player data.
        
        Returns:
            Dict[str, float]: Standard deviation per stat key — `strikeout_rate`, `walk_rate`, `isolated_power`, `on_base_percentage`, `base_running`. Each value will be `0.0` if insufficient data exists.
        """
        if self._league_std:
            return self._league_std.copy()
        snapshots = [self._extract_latest_stats(s) for s in self._players_seasons_data.values() if s]
        snapshots = [s for s in snapshots if s]
        return self._std_dicts(snapshots)

    async def get_league_weighted_std(self) -> Dict[str, float]:
        """
        Provide the league weighted standard deviations for tracked statistics (stub implementation).
        
        Returns:
            A dictionary mapping tracked stat keys (e.g., "strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running") to their weighted standard deviation as floats; currently returns an empty dictionary.
        """
        return {}

    def fetch_team_roster(self, team_id: int, season: int) -> Dict[str, Any]:
        """
        Return an empty roster mapping for the given team and season (stub implementation).
        
        Returns:
            dict: An empty dictionary representing the team's roster.
        """
        return {}

    # Helper methods for test setup and edge case creation for use case interactor unit testing
    def set_players_seasons_data(self, player_id: int, seasons: Dict):
        """
        Store seasons statistics for a player in the mock repository.
        
        Parameters:
            player_id (int): Unique identifier for the player.
            seasons (Dict): Mapping of season keys to that season's stats (e.g., {year: {stat_name: value}}). Existing data for the player is replaced.
        """
        self._players_seasons_data[player_id] = seasons
    
    def set_league_avg(self, league_avg: Dict[str, float]):
        """Set league average stats."""
        self._league_avg = league_avg.copy()
    
    def set_league_std(self, league_std: Dict[str, float]):
        """
        Store league standard deviation values for the repository.
        
        Makes an internal copy of the provided mapping from statistic names to their standard deviation values so later reads return an independent dictionary.
        
        Parameters:
            league_std (Dict[str, float]): Mapping of statistic keys to standard deviation values.
        """
        self._league_std = league_std.copy()

    # Internal helper methods (scoped to instance to avoid leaking globals)
    def _extract_latest_stats(self, seasons: Dict) -> Dict[str, float]:
        """
        Select the most recent season snapshot with plate appearances and return its key batting metrics as floats.
        
        Parameters:
            seasons (Dict): Mapping from season year (string keys) to a stats dictionary for that season.
        
        Returns:
            Dict[str, float]: A dict containing `strikeout_rate`, `walk_rate`, `isolated_power`, `on_base_percentage`, and `base_running` from the most recent season with `plate_appearances` > 0. Each value is coerced to float and missing or falsy values are returned as 0.0. Returns an empty dict if `seasons` is empty or no season has `plate_appearances` > 0.
        """
        if not seasons:
            return {}
        ordered = sorted((int(y) for y in seasons.keys()), reverse=True)
        for y in ordered:
            s = seasons[str(y)]
            if (s.get("plate_appearances", 0) or 0) > 0:
                return {
                    "strikeout_rate": float(s.get("strikeout_rate", 0.0) or 0.0),
                    "walk_rate": float(s.get("walk_rate", 0.0) or 0.0),
                    "isolated_power": float(s.get("isolated_power", 0.0) or 0.0),
                    "on_base_percentage": float(s.get("on_base_percentage", 0.0) or 0.0),
                    "base_running": float(s.get("base_running", 0.0) or 0.0),
                }
        return {}

    def _average_dicts(self, dicts: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Compute the element-wise average across a list of stat dictionaries.
        
        Parameters:
            dicts (List[Dict[str, float]]): List of dictionaries mapping stat names (e.g., "strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running") to numeric values. If the list is empty, defaults for the tracked stats are used.
        
        Returns:
            Dict[str, float]: Dictionary mapping each stat key (taken from the first dictionary in `dicts`) to its arithmetic mean across the input list. Missing keys in individual dictionaries are treated as 0.0; when `dicts` is empty, returns zeros for the tracked stats.
        """
        if not dicts:
            return {"strikeout_rate": 0, "walk_rate": 0, "isolated_power": 0, "on_base_percentage": 0, "base_running": 0}
        keys = dicts[0].keys()
        return {k: sum(d.get(k, 0.0) for d in dicts) / len(dicts) for k in keys}

    def _std_dicts(self, dicts: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Compute per-key standard deviations across a list of stat dictionaries.
        
        Parameters:
            dicts (List[Dict[str, float]]): A list of snapshots where each dictionary maps stat names
                (e.g., "strikeout_rate", "walk_rate", "isolated_power", "on_base_percentage", "base_running")
                to numeric values.
        
        Returns:
            Dict[str, float]: A mapping from each stat name present in the first dictionary to its
            population standard deviation across the provided snapshots. If `dicts` is empty, returns
            zeros for all tracked stats. If the computed standard deviation for a key is zero,
            the function returns 1e-9 for that key.
        """
        if not dicts:
            return {"strikeout_rate": 0, "walk_rate": 0, "isolated_power": 0, "on_base_percentage": 0, "base_running": 0}
        avg = self._average_dicts(dicts)
        out: Dict[str, float] = {}
        keys = dicts[0].keys()
        for k in keys:
            vals = [d.get(k, 0.0) for d in dicts]
            mean = avg[k]
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            out[k] = (var ** 0.5) or 10**-9
        return out

class MockPlayerRepository(PlayerRepository):
    """Mock implementation of PlayerRepository for testing."""
    
    def __init__(self):
        self._players: List[Dict] = []
        self._player_by_id: Dict[int, Dict] = {}
    
    async def get_all_players(self) -> List[Dict]:
        """Get all players from database."""
        return self._players.copy()
    
    async def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get a specific player by ID."""
        return self._player_by_id.get(player_id)
    
    def upload_team(self, team, team_name, final_players):
        pass
    
    def bulk_upsert_players(self, players: List[Dict[str, any]]) -> None:
        pass
    
    def set_league_averages(self, league_doc: Dict[str, any]) -> None:
        pass
    def build_player_image_url(self, player_id: int) -> str:
        """Return a player headshot URL."""
        return f"https://example.com/players/{player_id}.jpg"
    
    # heelper methods for test setup to add to in memory database 
    def add_player(self, player: Dict):
        """Add a player to the mock repository."""
        mlbam_id = player.get("mlbam_id")
        if mlbam_id:
            self._player_by_id[mlbam_id] = player
        self._players.append(player)
    
    def set_player(self, player_id: int, player: Dict):
        """
        Set or update a player in the repository by their ID.
        
        Parameters:
            player_id (int): Unique identifier for the player.
            player (Dict): Player data to store or replace for the given ID.
        """
        self._player_by_id[player_id] = player

async def fetch_league_vectors(repo: RosterRepository) -> tuple[Dict[str, float], Dict[str, float]]:
    """
    Fetches the league unweighted average and unweighted standard deviation vectors from a roster repository.
    
    Parameters:
        repo (RosterRepository): Repository providing league statistics.
    
    Returns:
        tuple[Dict[str, float], Dict[str, float]]: A tuple (unweighted_avg, unweighted_std) where
            unweighted_avg maps statistic names to their league unweighted averages and
            unweighted_std maps statistic names to their league unweighted standard deviations.
    """
    return await repo.get_league_unweighted_average(), await repo.get_league_unweighted_std()
