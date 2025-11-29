import types
from typing import Any, Dict, List, Optional

import pandas as pd
import pytest

import scripts.get_players as gp


class DummyRosterRepo:
    def __init__(self, roster: Optional[Dict[str, Any]] = None):
        self._roster = roster or {}

    def fetch_team_roster(self, team_id: int, year: int) -> Dict[str, Any]:
        return self._roster


class DummyPlayerRepo:
    def __init__(self):
        self.upserts: List[List[Dict[str, Any]]] = []

    def bulk_upsert_players(self, players: List[Dict[str, Any]]) -> None:
        self.upserts.append(players)


def test_get_team_roster_positions_basic(monkeypatch):
    monkeypatch.setattr(gp, "TEAM_IDS", [999])
    roster_repo = DummyRosterRepo(
        {
            "roster": [
                {"person": {"id": 10}, "position": {"abbreviation": "CF"}},
                {"person": {"id": 11}, "position": {"abbreviation": "1B"}},
            ]
        }
    )

    result = gp.get_team_roster_positions(roster_repo, 2024)

    assert result == {10: "CF", 11: "1B"}


def test_get_team_roster_positions_skips_missing(monkeypatch):
    monkeypatch.setattr(gp, "TEAM_IDS", [999])
    roster_repo = DummyRosterRepo({"roster": [{"person": {}, "position": {}}]})

    result = gp.get_team_roster_positions(roster_repo, 2024)

    assert result == {}


def test_get_player_stats_for_year_happy_path():
    df = pd.DataFrame(
        [
          {
              "IDfg": 1,
              "PA": 120,
              "G": 10,
              "AB": 100,
              "H": 50,
              "1B": 30,
              "2B": 10,
              "3B": 5,
              "HR": 5,
              "R": 20,
              "RBI": 25,
              "BB": 12,
              "SO": 18,
              "SB": 3,
              "CS": 1,
              "AVG": 0.300,
              "OBP": 0.350,
              "SLG": 0.450,
              "OPS": 0.800,
              "ISO": 0.150,
              "BABIP": 0.310,
              "BB%": 10,
              "K%": 15,
              "BB/K": 0.5,
              "wOBA": 0.340,
              "wRC+": 120,
              "WAR": 2.0,
              "Off": 5.0,
              "Def": 1.0,
              "BsR": 0.7,
              "Team": "ABC",
              "Hard%": 40,
              "Barrel%": 8,
              "EV": 90.0,
              "LA": 12.0,
          }
        ]
    )

    stats = gp.get_player_stats_for_year(1, df)

    assert stats is not None
    assert stats["plate_appearances"] == 120
    assert stats["walk_rate"] == 0.10
    assert stats["strikeout_rate"] == 0.15
    assert stats["team_abbrev"] == "ABC"


def test_get_player_stats_for_year_requires_min_pa():
    df = pd.DataFrame([{"IDfg": 1, "PA": 10}])
    assert gp.get_player_stats_for_year(1, df) is None


def test_build_all_seasons_uses_cache(monkeypatch):
    calls: List[int] = []

    def fake_get_stats(fg_id: int, df: Any):
        calls.append(df)
        return {"stat": df}

    monkeypatch.setattr(gp, "get_player_stats_for_year", fake_get_stats)

    yearly_cache = {2023: "df2023", 2024: "df2024"}
    seasons = gp.build_all_seasons(1, yearly_cache, 2023, 2024)

    assert seasons == {"2023": {"stat": "df2023"}, "2024": {"stat": "df2024"}}
    assert calls == ["df2023", "df2024"]


def test_refresh_players_inserts_players(monkeypatch):
    # Stub batting_stats to return a minimal DataFrame
    df = pd.DataFrame([{"IDfg": 1, "Name": "Player One"}])
    monkeypatch.setattr(gp, "batting_stats", lambda season, qual=0: df)

    # Stub lookup to return mlbam id
    def fake_lookup(ids, key_type="fangraphs"):
        return pd.DataFrame([{"key_mlbam": 123, "key_fangraphs": ids[0]}])

    monkeypatch.setattr(gp, "playerid_reverse_lookup", fake_lookup)

    # Stub build_all_seasons to provide seasons with wRC+ and team
    monkeypatch.setattr(
        gp, "build_all_seasons", lambda fg_id, cache, start_year, current_season: {
            str(current_season): {"wrc_plus": 110.0, "team_abbrev": "XYZ"}
        }
    )

    # Stub positions
    monkeypatch.setattr(gp, "get_team_roster_positions", lambda repo, year: {123: "CF"})

    player_repo = DummyPlayerRepo()
    roster_repo = DummyRosterRepo()

    count = gp.refresh_players(player_repo, roster_repo, start_year=2024, current_season=2024)

    assert count == 1
    assert len(player_repo.upserts) == 1
    player = player_repo.upserts[0][0]
    assert player["mlbam_id"] == 123
    assert player["fangraphs_id"] == 1
    assert player["position"] == "CF"
