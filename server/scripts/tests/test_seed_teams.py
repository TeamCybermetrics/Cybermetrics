from typing import Any, Dict, List, Tuple

import pandas as pd
import pytest

import scripts.seed_teams as st


class DummyRosterRepo:
    def __init__(self, roster: Dict[str, Any]):
        self._roster = roster

    def fetch_team_roster(self, team_id: int, year: int) -> Dict[str, Any]:
        return self._roster


class DummyPlayerRepo:
    def __init__(self):
        self.uploads: List[Tuple[str, str, List[Dict[str, Any]]]] = []

    def upload_team(self, team_code: str, team_name: str, players: List[Dict[str, Any]]) -> None:
        self.uploads.append((team_code, team_name, players))


def test_upload_positional_players_selects_best_and_adds_dh(monkeypatch):
    # Limit teams to a test code
    monkeypatch.setattr(st, "team_ids", {"TST": 1})
    monkeypatch.setattr(st, "team_names", {"TST": "Testers"})

    # Fake roster with two CF candidates and one 1B
    roster_repo = DummyRosterRepo(
        {
            "roster": [
                {"person": {"id": 1, "fullName": "CF One"}, "position": {"abbreviation": "CF"}},
                {"person": {"id": 2, "fullName": "CF Two"}, "position": {"abbreviation": "CF"}},
                {"person": {"id": 3, "fullName": "1B One"}, "position": {"abbreviation": "1B"}},
                {"person": {"id": 4, "fullName": "Util"}, "position": {"abbreviation": "RF"}},
            ]
        }
    )

    # Stub fangraphs id and stats: make player 2 the best CF, player 3 good, player 4 used for DH
    monkeypatch.setattr(st, "get_fangraphs_id", lambda mlbam: mlbam)

    def fake_stats(fg_id: int, league_df: Any) -> Dict[str, float]:
        # Make CF Two (id 2) the best CF; Util (id 4) highest overall for DH
        base_iso = 4.0
        return {
            "strikeout_rate": 1.0,
            "walk_rate": 2.0 if fg_id != 2 else 5.0,
            "on_base_percentage": 3.0,
            "isolated_power": 10.0 if fg_id == 4 else base_iso,
            "base_running": 5.0,
        }

    monkeypatch.setattr(st, "get_player_stats", fake_stats)

    # Make 2 > 1 for CF via offensive_player_score; 4 has highest score overall and should become DH
    result = st.upload_positional_players("TST", 2024, pd.DataFrame(), roster_repo)

    team_code, team_name, players = result
    assert team_code == "TST"
    assert team_name == "Testers"

    positions = {p["position"]: p["mlbam_id"] for p in players}
    # Best CF should be id 2; 1B should be id 3; RF should be id 4.
    # DH fallback comes from the remaining highest (id 1).
    assert positions["CF"] == 2
    assert positions["1B"] == 3
    assert positions["RF"] == 4
    assert positions["DH"] == 1


def test_seed_all_teams_uploads_each_team(monkeypatch):
    monkeypatch.setattr(st, "team_abbrev", ["T1", "T2"])
    monkeypatch.setattr(st, "team_ids", {"T1": 1, "T2": 2})
    monkeypatch.setattr(st, "team_names", {"T1": "Team One", "T2": "Team Two"})

    # Stub batting_stats to return a dummy DataFrame
    monkeypatch.setattr(st, "batting_stats", lambda year, qual=0: pd.DataFrame())

    # Stub upload_positional_players to return one player per team
    def fake_upload(team, year, league_df, roster_repo):
        return (team, st.team_names[team], [{"mlbam_id": 1, "position": "CF", "overall_score": 10}])

    monkeypatch.setattr(st, "upload_positional_players", fake_upload)

    player_repo = DummyPlayerRepo()
    roster_repo = DummyRosterRepo({})

    st.seed_all_teams(player_repo, roster_repo, 2024)

    # Both teams should be uploaded
    assert len(player_repo.uploads) == 2
    codes = {u[0] for u in player_repo.uploads}
    assert codes == {"T1", "T2"}
