import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Optional, Dict, List
from config.firebase import firebase_service  
from pybaseball import playerid_reverse_lookup, batting_stats

current_season = 2024
start_year = 2015  # Fetch stats from 2015 onwards


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


def get_player_stats_for_year(fangraphs_id: int, year: int, batting_stats_df) -> Optional[Dict]:
    """Get player stats for a specific year with all available stats"""
    player_stat = batting_stats_df[batting_stats_df['IDfg'] == fangraphs_id]

    if player_stat.empty:
        return None
    player_stat_row = player_stat.iloc[0]

    # Filter out players with minimal plate appearances (likely pitchers)
    # Require at least 50 PA to have meaningful stats
    plate_appearances = player_stat_row.get('PA', 0)
    if plate_appearances < 50:
        return None

    team = player_stat_row['Team']
    
    # Helper function to safely get float values
    def safe_float(key, default=0.0):
        try:
            val = player_stat_row.get(key, default)
            return float(val) if val != '' and str(val) != 'nan' else default
        except:
            return default
    
    def safe_int(key, default=0):
        try:
            val = player_stat_row.get(key, default)
            return int(val) if val != '' and str(val) != 'nan' else default
        except:
            return default
    
    return {
        # Basic counting stats
        "games": safe_int('G'),
        "plate_appearances": safe_int('PA'),
        "at_bats": safe_int('AB'),
        "hits": safe_int('H'),
        "singles": safe_int('1B'),
        "doubles": safe_int('2B'),
        "triples": safe_int('3B'),
        "home_runs": safe_int('HR'),
        "runs": safe_int('R'),
        "rbi": safe_int('RBI'),
        "walks": safe_int('BB'),
        "strikeouts": safe_int('SO'),
        "stolen_bases": safe_int('SB'),
        "caught_stealing": safe_int('CS'),
        
        # Rate stats (percentages)
        "batting_average": safe_float('AVG'),
        "on_base_percentage": safe_float('OBP'),
        "slugging_percentage": safe_float('SLG'),
        "ops": safe_float('OPS'),
        "isolated_power": safe_float('ISO'),
        "babip": safe_float('BABIP'),
        
        # Plate discipline
        "walk_rate": safe_float('BB%') / 100,
        "strikeout_rate": safe_float('K%') / 100,
        "bb_k_ratio": safe_float('BB/K'),
        
        # Advanced metrics
        "woba": safe_float('wOBA'),
        "wrc_plus": safe_float('wRC+'),
        "war": safe_float('WAR'),
        "off": safe_float('Off'),
        "def": safe_float('Def'),
        "base_running": safe_float('BsR'),
        
        # Contact quality
        "hard_hit_rate": safe_float('Hard%') / 100 if 'Hard%' in player_stat_row else None,
        "barrel_rate": safe_float('Barrel%') / 100 if 'Barrel%' in player_stat_row else None,
        "avg_exit_velocity": safe_float('EV') if 'EV' in player_stat_row else None,
        "avg_launch_angle": safe_float('LA') if 'LA' in player_stat_row else None,
        
        # Team
        "team_abbrev": team if team != "- - -" else None
    }


def get_all_player_seasons(fangraphs_id: int, player_name: str, yearly_stats_cache: Dict[int, any]) -> Dict[str, Dict]:
    """Get stats for all seasons a player has played"""
    all_seasons = {}
    
    for year in range(start_year, current_season + 1):
        try:
            year_stats = yearly_stats_cache.get(year)
            if year_stats is None:
                continue
                
            stats = get_player_stats_for_year(fangraphs_id, year, year_stats)
            
            if stats:
                all_seasons[str(year)] = stats
        except Exception as e:
            continue
    
    return all_seasons


def upload_all_players() -> None:
    """
    Upload all MLB players (including free agents) to Firestore
    Fetches all seasons for each player
    """
    
    db = firebase_service.db
    
    if not db:
        print("Firebase not configured")
        return
    
    # Pre-fetch all yearly stats (this is the optimization!)
    print(f"{'='*60}")
    print("Pre-fetching batting stats for all years (this takes a moment)...")
    print(f"{'='*60}\n")
    
    yearly_stats_cache = {}
    for year in range(start_year, current_season + 1):
        print(f"Fetching {year} batting stats...")
        try:
            yearly_stats_cache[year] = batting_stats(year, qual=0)
            print(f"  ✓ Loaded {len(yearly_stats_cache[year])} players for {year}")
        except Exception as e:
            print(f"  ✗ Error loading {year}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Cached stats for {len(yearly_stats_cache)} years")
    print(f"{'='*60}\n")
    
    # Get current season players as base list
    print(f"Processing players from {current_season} season...")
    current_batting_stats = yearly_stats_cache.get(current_season)
    if current_batting_stats is None:
        print("Error: Could not load current season stats")
        return
    
    print(f"Total players in {current_season}: {len(current_batting_stats)}\n")
    
    all_players = []
    processed_count = 0
    
    for idx, row in current_batting_stats.iterrows():
        fangraphs_id = int(row['IDfg'])
        player_name = row['Name']
        current_team = row['Team']
        
        processed_count += 1
        print(f"\n[{processed_count}/{len(current_batting_stats)}] Processing {player_name} ({fangraphs_id})...")
        
        # Try to get MLBAM ID
        try:
            result_df = playerid_reverse_lookup([fangraphs_id], key_type="fangraphs")
            if result_df.empty:
                print(f"  Skipping - no MLBAM ID found")
                continue
            
            mlbam_id = result_df.iloc[0]["key_mlbam"]
            if str(mlbam_id) == "nan":
                print(f"  Skipping - invalid MLBAM ID")
                continue
            
            mlbam_id = int(mlbam_id)
        except Exception as e:
            print(f"  Skipping - error getting MLBAM ID: {e}")
            continue
        
        # Get all seasons for this player
        all_seasons = get_all_player_seasons(fangraphs_id, player_name, yearly_stats_cache)
        
        if not all_seasons:
            print(f"  Skipping - no meaningful stats (likely pitcher or < 50 PA)")
            continue
        
        # Get current team abbreviation
        team_abbrev = current_team if current_team != "- - -" else None
        
        # Get most recent wRC+ as overall_score (no calculation, just raw stat)
        most_recent_year = max(all_seasons.keys())
        overall_score = all_seasons[most_recent_year].get("wrc_plus", 0)
        
        player_data = {
            "mlbam_id": mlbam_id,
            "fangraphs_id": fangraphs_id,
            "name": player_name,
            "team_abbrev": team_abbrev,
            "overall_score": overall_score,
            "seasons": all_seasons
        }
        
        all_players.append(player_data)
        print(f"  ✓ Added: {player_name} - Team: {team_abbrev or 'Free Agent'} - wRC+: {overall_score} - Seasons: {len(all_seasons)}")
    
    print(f"\n{'='*60}")
    print(f"Uploading {len(all_players)} players to Firebase...")
    print(f"{'='*60}\n")
    
    # Upload each player to the players collection
    for i, player in enumerate(all_players, 1):
        player_id = str(player["mlbam_id"])
        db.collection("players").document(player_id).set(player)
        print(f"[{i}/{len(all_players)}] Uploaded {player['name']}")
    
    print(f"\n{'='*60}")
    print(f"Successfully uploaded {len(all_players)} players!")
    print(f"{'='*60}")


if __name__ == "__main__":
    upload_all_players()
