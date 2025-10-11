import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List
from config.firebase import firebase_service  
from pybaseball import playerid_reverse_lookup
import requests

season = 2025

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


def get_fangraphs_ids(mlbam_ids: List[int]) -> Dict[int, int]:
    """Convert list of MLBAM IDs to a dictionary mapping MLBAM -> FanGraphs ID"""

    fangraphs_map = {}
    
    try:
        result_df = playerid_reverse_lookup(mlbam_ids, key_type="mlbam")
        for index in range(len(result_df)):
            mlbam_id = result_df.iloc[index]["key_mlbam"]
            fangraphs_id = result_df.iloc[index]["key_fangraphs"]
            if str(fangraphs_id) != "nan":
                fangraphs_map[mlbam_id] = int(fangraphs_id)
    except Exception:
        pass
    
    return fangraphs_map


def upload_positional_players(team: str, year: int) -> None:
    """Upload positional players for a team to Firestore"""
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
    
    for player in roster:
        person = player.get('person', {})
        position_info = player.get('position', {})
        position = position_info.get('abbreviation', '')

        if position == 'P':
            continue

        mlbam_id = person.get('id')

        if not mlbam_id:
            continue

        player_data = {
            "mlbam_id": mlbam_id,
            "name": person.get('fullName', ''),
            "position": position,
        }
        pos_players.append(player_data)
        mlbam_ids.append(mlbam_id)
    
    fangraphs_map = get_fangraphs_ids(mlbam_ids)
    
    final_players = []
    
    for player_data in pos_players:
        mlbam_id = player_data["mlbam_id"]
        fangraphs_id = None

        if mlbam_id in fangraphs_map:
            fangraphs_id = fangraphs_map[mlbam_id]
        
        final_player = {
            "mlbam_id": mlbam_id,
            "fangraphs_id": fangraphs_id,
            "name": player_data["name"],
            "position": player_data["position"],
        }
        
        final_players.append(final_player)
    
    if final_players != []:
        db.collection("teams").document(team.upper()).set({
            "full_team_name": team_names.get(team),
            "positional_players": final_players
        }, merge=True)


for team in team_abbrev:
    upload_positional_players(team, season)

