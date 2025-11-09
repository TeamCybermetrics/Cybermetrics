from typing import Dict, List, Optional, Tuple
from pybaseball import playerid_reverse_lookup, batting_stats
import requests
from server.repositories.player_repository import PlayerRepository  # use package-qualified import

season = 2024

team_abbrev = [
    "ARI","ATL","BAL","BOS","CHC","CIN","CLE","COL","CWS","DET",
    "HOU","KC","LAA","LAD","MIA","MIL","MIN","NYM","NYY","OAK",
    "PHI","PIT","SD","SEA","SF","STL","TB","TEX","TOR","WSH"
]

team_ids: Dict[str, int] = {
    "ARI": 109, "ATL": 144, "BAL": 110, "BOS": 111, "CHC": 112,
    "CIN": 113, "CLE": 114, "COL": 115, "CWS": 145, "DET": 116,
    "HOU": 117, "KC": 118, "LAA": 108, "LAD": 119, "MIA": 146,
    "MIL": 158, "MIN": 142, "NYM": 121, "NYY": 147, "OAK": 133,
    "PHI": 143, "PIT": 134, "SD": 135, "SEA": 136, "SF": 137,
    "STL": 138, "TB": 139, "TEX": 140, "TOR": 141, "WSH": 120
}

team_names: Dict[str, str] = {
    "ARI": "Arizona Diamondbacks","ATL": "Atlanta Braves","BAL": "Baltimore Orioles","BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs","CIN": "Cincinnati Reds","CLE": "Cleveland Guardians","COL": "Colorado Rockies",
    "CWS": "Chicago White Sox","DET": "Detroit Tigers","HOU": "Houston Astros","KC": "Kansas City Royals",
    "LAA": "Los Angeles Angels","LAD": "Los Angeles Dodgers","MIA": "Miami Marlins","MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins","NYM": "New York Mets","NYY": "New York Yankees","OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies","PIT": "Pittsburgh Pirates","SD": "San Diego Padres","SEA": "Seattle Mariners",
    "SF": "San Francisco Giants","STL": "St. Louis Cardinals","TB": "Tampa Bay Rays","TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays","WSH": "Washington Nationals"
}

allowed_positions = {"C","1B","2B","3B","SS","LF","CF","RF","DH","TWP"}

def get_fangraphs_id(mlbam_id: int) -> Optional[int]:
    try:
        result_df = playerid_reverse_lookup([mlbam_id], key_type="mlbam")
        if not result_df.empty:
            fangraphs_id = result_df.iloc[0]["key_fangraphs"]
            if str(fangraphs_id) != "nan":
                return int(fangraphs_id)
    except Exception:
        pass
    return None

def get_player_stats(fangraphs_id: int, league_df) -> Optional[dict[str, float]]:
    player_stat = league_df[league_df['IDfg'] == fangraphs_id]
    if player_stat.empty:
        return None
    r = player_stat.iloc[0]
    try:
        return {
            "strikeout_rate": 1.0 - float(r['K%']) / 100.0,
            "walk_rate": float(r['BB%']) / 100.0,
            "on_base_percentage": float(r['OBP']),
            "isolated_power": float(r['ISO']),
            "base_running": float(r['BsR']),
        }
    except Exception:
        return None

def offensive_player_score(s: dict[str, float]) -> float:
    return s["strikeout_rate"] + s["walk_rate"] + s["on_base_percentage"] + s["isolated_power"] + s["base_running"]

def upload_positional_players(team: str, year: int, league_df) -> Tuple[str, str, List[dict]]:
    result: Dict[str, dict] = {}
    team_id = team_ids.get(team)
    if not team_id:
        return (team, team_names.get(team, ""), [])

    api_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/Active"
    resp = requests.get(api_url, params={"season": year}, timeout=15)
    resp.raise_for_status()
    roster = resp.json().get('roster', []) or []

    all_player_scores: List[dict] = []

    for player in roster:
        person = player.get('person', {})
        position = player.get('position', {}).get('abbreviation', '')
        if position not in allowed_positions:
            continue

        mlbam_id = person.get('id')
        if not mlbam_id:
            continue

        fangraphs_id = get_fangraphs_id(int(mlbam_id))
        if not fangraphs_id:
            continue

        stats = get_player_stats(fangraphs_id, league_df)
        if not stats:
            continue

        score = offensive_player_score(stats)
        player_data = {
            "mlbam_id": int(mlbam_id),
            "fangraphs_id": int(fangraphs_id),
            "name": person.get('fullName', ''),
            "position": position,
            "overall_score": score,
        }
        if position != "TWP":
            if position not in result or score > result[position]["overall_score"]:
                result[position] = player_data
        all_player_scores.append(player_data)

    final_players = [result[p] for p in result]

    if not any(p["position"] == "DH" for p in final_players):
        remaining = [p for p in all_player_scores if p not in final_players]
        remaining.sort(key=lambda x: x["overall_score"], reverse=True)
        if remaining:
            dh = dict(remaining[0])
            dh["position"] = "DH"
            final_players.append(dh)

    team_name = team_names.get(team, "")
    return (team, team_name, final_players)

def seed_all_teams(repo: PlayerRepository, year: int) -> None:
    league_df = batting_stats(year, qual=0)
    for team in team_abbrev:
        team_upload = upload_positional_players(team, year, league_df)
        team_code, team_name, players = team_upload
        if not players:
            continue
        try:
            repo.upload_team(team_code, team_name, players)
        except TypeError:
            repo.upload_team(team_upload)


if __name__ == "__main__":
    raise SystemExit("Use a runner or scheduler to inject PlayerRepository.")