import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List
from server.config.firebase import firebase_service  
from pybaseball import playerid_reverse_lookup, batting_stats
import requests
from typing import Optional

season = 2024

team_abbrev = [
    "ARI","ATL","BAL","BOS","CHC","CIN","CLE","COL","CWS","DET",
    "HOU","KC","LAA","LAD","MIA","MIL","MIN","NYM","NYY","OAK",
    "PHI","PIT","SD","SEA","SF","STL","TB","TEX","TOR","WSH"
]

team_ids = {
    "ARI": 109, "ATL": 144, "BAL": 110, "BOS": 111, "CHC": 112,
    "CIN": 113, "CLE": 114, "COL": 115, "CWS": 145, "DET": 116,
    "HOU": 117, "KC": 118, "LAA": 108, "LAD": 119, "MIA": 146,
    "MIL": 158, "MIN": 142, "NYM": 121, "NYY": 147, "OAK": 133,
    "PHI": 143, "PIT": 134, "SD": 135, "SEA": 136, "SF": 137,
    "STL": 138, "TB": 139, "TEX": 140, "TOR": 141, "WSH": 120
}
team_names = {
    "ARI": "Arizona Diamondbacks",
      "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "CWS": "Chicago White Sox",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KC": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SD": "San Diego Padres",
    "SEA": "Seattle Mariners",
    "SF": "San Francisco Giants",
    "STL": "St. Louis Cardinals",
    "TB": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSH": "Washington Nationals"
}

batting_stats_league = batting_stats(season, qual=0)

all_positions = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]


def get_fangraphs_id(mlbam_id: int) -> Optional[int]:
    """Convert single MLBAM ID to FanGraphs ID"""
    
    try:
        result_df = playerid_reverse_lookup([mlbam_id], key_type="mlbam")
        if not result_df.empty:
            fangraphs_id = result_df.iloc[0]["key_fangraphs"]
            if str(fangraphs_id) != "nan":
                return int(fangraphs_id)
    except Exception:
        pass
    
    return None

def get_player_stats(fangraphs_id: int) -> Optional[dict[str, int]]:
    """ Takes in a fangraph id and uses the Fangraphs data to return a dictionary of the players 
    batting average, on base percentage, isolated power, baserunning 
    and strikeout rate """
    player_stat = batting_stats_league[batting_stats_league['IDfg'] == fangraphs_id]

    if player_stat.empty:
        return None
    player_stat_row = player_stat.iloc[0]

    return {
        "strikeout_rate":  1 - (float(player_stat_row['K%']) / 100),
        "walk_rate": float(player_stat_row['BB%']) / 100,
        "on_base_percentage": float(player_stat_row['OBP']),
        "isolated_power": float(player_stat_row['ISO']),
        "base_running": float(player_stat_row['BsR'])
    }

def offensive_player_score(player_stats: dict[str, int] ) -> int:
    """
    Takes in a player and compute there overal offensive stat using 
    batting average, on base percentage, isolated power, baserunning 
    and strikeout rate
    """

    return player_stats["strikeout_rate"] + player_stats["walk_rate"] + player_stats["on_base_percentage"] + player_stats["isolated_power"] + player_stats["base_running"]


def upload_positional_players(team: str, year: int) -> None:
    """
    Upload positional players for a team to Firestore
    """

    result ={}
    db = firebase_service.db
    
    if not db:
        return
    
    team_id = team_ids.get(team)

    if not team_id:
        return
    
    api_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/Active"
    response = requests.get(api_url, params={"season": year})
    data = response.json()
    roster = data.get('roster', [])
    pos_players = []
    mlbam_ids = []
    all_player_scores = []

    for player in roster:
        person = player.get('person', {})
        position_info = player.get('position', {})
        position = position_info.get('abbreviation', '')

        if position not in ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", "TWP"]:
            continue

        mlbam_id = person.get('id')

        if not mlbam_id:
            continue
        
        fangraphs_id = get_fangraphs_id(mlbam_id)

        if not fangraphs_id:
            continue
        
        player_stat = get_player_stats(fangraphs_id)
        if player_stat is None:
            continue
        player_overall_score = offensive_player_score(player_stat)

        player_data = {
            "mlbam_id": mlbam_id,
            "fangraphs_id": fangraphs_id,
            "name": person.get('fullName', ''),
            "position": position,
            "overall_score": player_overall_score

        }
        if position not in result or player_data["overall_score"] > result[position]["overall_score"]:
            result[position] = player_data
        all_player_scores.append(player_data)

    final_players = [result[x] for x in result]

    has_dh = False
    for player in final_players:
        if player["position"] == "DH":
            has_dh = True

    if not has_dh:
        players_cut = [player for player in all_player_scores if player not in final_players]
        players_cut.sort(key=lambda player:player["overall_score"], reverse=True)
        if players_cut != []:
            dh_player = players_cut[0]
            final_players.append({
                "mlbam_id": dh_player["mlbam_id"],
                "fangraphs_id": dh_player["fangraphs_id"],
                "name": dh_player["name"],
                "position": "DH",
                "overall_score": dh_player["overall_score"]
            })

    if final_players != []:
        db.collection("teams").document(team.upper()).set({
            "full_team_name": team_names.get(team),
            "positional_players": final_players,
            "number": len(final_players)
        }, merge=True)

for team in team_abbrev:
    upload_positional_players(team, season)