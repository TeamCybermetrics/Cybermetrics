from typing import Optional, Dict, List, Any
from pybaseball import playerid_reverse_lookup, batting_stats
from repositories.player_repository import PlayerRepository

def get_fangraphs_id(mlbam_id: int) -> Optional[int]:
    try:
        df = playerid_reverse_lookup([mlbam_id], key_type="mlbam")
        if df.empty:
            return None
        v = df.iloc[0]["key_fangraphs"]
        return int(v) if str(v) != "nan" else None
    except Exception:
        return None

def get_player_stats_for_year(fg_id: int, year_df) -> Optional[Dict[str, Any]]:
    row = year_df[year_df["IDfg"] == fg_id]
    if row.empty:
        return None
    r = row.iloc[0]
    pa = r.get("PA", 0) or 0
    if pa < 50:
        return None

    def f(key: str, d: float = 0.0) -> float:
        try:
            v = r.get(key, d)
            return float(v) if v not in ("", None) and str(v) != "nan" else d
        except Exception:
            return d

    def i(key: str, d: int = 0) -> int:
        try:
            v = r.get(key, d)
            return int(v) if v not in ("", None) and str(v) != "nan" else d
        except Exception:
            return d

    team = r.get("Team")
    return {
        "games": i("G"),
        "plate_appearances": i("PA"),
        "at_bats": i("AB"),
        "hits": i("H"),
        "singles": i("1B"),
        "doubles": i("2B"),
        "triples": i("3B"),
        "home_runs": i("HR"),
        "runs": i("R"),
        "rbi": i("RBI"),
        "walks": i("BB"),
        "strikeouts": i("SO"),
        "stolen_bases": i("SB"),
        "caught_stealing": i("CS"),
        "batting_average": f("AVG"),
        "on_base_percentage": f("OBP"),
        "slugging_percentage": f("SLG"),
        "ops": f("OPS"),
        "isolated_power": f("ISO"),
        "babip": f("BABIP"),
        "walk_rate": f("BB%") / 100.0,
        "strikeout_rate": f("K%") / 100.0,
        "bb_k_ratio": f("BB/K"),
        "woba": f("wOBA"),
        "wrc_plus": f("wRC+"),
        "war": f("WAR"),
        "off": f("Off"),
        "def": f("Def"),
        "base_running": f("BsR"),
        "hard_hit_rate": f("Hard%") / 100.0 if "Hard%" in r else None,
        "barrel_rate": f("Barrel%") / 100.0 if "Barrel%" in r else None,
        "avg_exit_velocity": f("EV") if "EV" in r else None,
        "avg_launch_angle": f("LA") if "LA" in r else None,
        "team_abbrev": team if team and team != "- - -" else None,
    }

def build_all_seasons(fg_id: int, yearly_cache: Dict[int, Any], start_year: int, current_season: int) -> Dict[str, Dict]:
    seasons: Dict[str, Dict] = {}
    for y in range(start_year, current_season + 1):
        df = yearly_cache.get(y)
        if df is None:
            continue
        stats = get_player_stats_for_year(fg_id, df)
        if stats:
            seasons[str(y)] = stats
    return seasons

def refresh_players(repo: PlayerRepository, start_year: int = 2015, current_season: int = 2024) -> int:
    yearly_cache: Dict[int, Any] = {}
    for y in range(start_year, current_season + 1):
        try:
            yearly_cache[y] = batting_stats(y, qual=0)
        except Exception:
            yearly_cache[y] = None

    current_df = yearly_cache.get(current_season)
    if current_df is None:
        return 0

    players: List[Dict[str, Any]] = []
    for _, row in current_df.iterrows():
        try:
            fg_id = int(row["IDfg"])
        except Exception:
            continue
        # Resolve MLBAM via fangraphs lookup
        try:
            lookup = playerid_reverse_lookup([fg_id], key_type="fangraphs")
            if lookup.empty:
                continue
            mlbam = lookup.iloc[0]["key_mlbam"]
            if str(mlbam) == "nan":
                continue
            mlbam = int(mlbam)
        except Exception:
            continue

        seasons = build_all_seasons(fg_id, yearly_cache, start_year, current_season)
        if not seasons:
            continue

        latest_year = max(seasons.keys(), key=int)
        overall = seasons[latest_year].get("wrc_plus", 0.0)
        players.append({
            "mlbam_id": mlbam,
            "fangraphs_id": fg_id,
            "name": row.get("Name", "Unknown"),
            "team_abbrev": seasons[latest_year].get("team_abbrev"),
            "overall_score": overall,
            "seasons": seasons,
        })

    if players:
        repo.bulk_upsert_players(players)
    return len(players)