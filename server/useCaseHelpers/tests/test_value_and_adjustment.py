"""
Unit tests for adjustment and value score logic in `RosterDomain`.
"""
import pytest
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.errors import InputValidationError
from services.tests.mocks.mock_repositories import (
    MockRosterRepository,
    fetch_league_vectors,
)
from services.tests.mocks.repository_test_utils import build_fake_players
from useCaseHelpers.tests.value_adjustment_utils import manual_contrib


class TestComputeAdjustmentSum:
    """Tests for `compute_adjustment_sum` covering direction, weighting & edge cases."""

    @pytest.fixture
    def domain(self):
        return RosterDomain()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_expected_contributions(self, domain):
        players = build_fake_players()
        repo = MockRosterRepository()
        # load seasons into mock
        for pid, seasons in players.items():
            repo.set_players_seasons_data(pid, seasons)
        league_avg, league_std = await fetch_league_vectors(repo)
        # Build team weakness from all players
        seasons_map = await repo.get_players_seasons_data(list(players.keys()))
        roster_resp = domain.calculate_roster_averages(seasons_map)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        team_weakness = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        # Choose one player's latest stats
        player_stats = {
            k: v for k, v in players[101]["2023"].items() if k in team_avg.keys()
        }
        adj_sum, contribs = domain.compute_adjustment_sum(
            player_latest_stats=player_stats,
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        manual_sum, manual_contribs = manual_contrib(player_stats, league_avg, league_std, team_weakness)

        assert adj_sum == pytest.approx(manual_sum)
        assert contribs["strikeout_rate"] == pytest.approx(manual_contribs["strikeout_rate"])  # league - player
        assert contribs["walk_rate"] == pytest.approx(manual_contribs["walk_rate"])  # player - league

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_negative_weights_uses_abs(self, domain):
        # Use real league vectors then inject a negative weakness
        players = build_fake_players()
        repo = MockRosterRepository()
        for pid, seasons in players.items():
            repo.set_players_seasons_data(pid, seasons)
        league_avg, league_std = await fetch_league_vectors(repo)
        team_weakness = {"walk_rate": -1.0}
        player_stats = {"walk_rate": 0.11}
        adj_sum, contribs = domain.compute_adjustment_sum(
            player_latest_stats=player_stats,
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        assert contribs["walk_rate"] == pytest.approx(3.0)
        assert adj_sum == pytest.approx(3.0)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_zero_std_raises(self, domain):
        # Force std to zero for a single stat
        player_stats = {"isolated_power": 0.17}
        league_avg = {"isolated_power": 0.16}
        league_std = {"isolated_power": 0.0}
        team_weakness = {"isolated_power": 0.5}
        with pytest.raises(ZeroDivisionError):
            domain.compute_adjustment_sum(
                player_latest_stats=player_stats,
                league_avg=league_avg,
                league_std=league_std,
                team_weakness=team_weakness,
            )


class TestComputeValueScore:
    """Tests for `compute_value_score` composition and validation paths."""

    @pytest.fixture
    def domain(self):
        return RosterDomain()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_value_score_composition(self, domain):
        players = build_fake_players()
        repo = MockRosterRepository()
        for pid, seasons in players.items():
            repo.set_players_seasons_data(pid, seasons)
        seasons_map = await repo.get_players_seasons_data(list(players.keys()))
        roster_resp = domain.calculate_roster_averages(seasons_map)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        league_avg, league_std = await fetch_league_vectors(repo)
        team_weakness = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        # pick player 101
        latest_war = players[101]["2023"].get("war", 0.0)
        player_stats = {
            k: v for k, v in players[101]["2023"].items() if k in team_avg.keys()
        }
        adj_sum, _ = domain.compute_adjustment_sum(
            player_latest_stats=player_stats,
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        vs = domain.compute_value_score(
            latest_war=latest_war,
            player_latest_stats=player_stats,
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        assert vs["adjustment_score"] == pytest.approx(adj_sum)
        assert vs["value_score"] == pytest.approx(round(latest_war + adj_sum, 3))
        assert set(vs["contributions"].keys()) == set(player_stats.keys())

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_war_raises(self, domain):
        players = build_fake_players()
        repo = MockRosterRepository()
        for pid, seasons in players.items():
            repo.set_players_seasons_data(pid, seasons)
        league_avg, league_std = await fetch_league_vectors(repo)
        player_stats = {k: v for k, v in players[101]["2023"].items() if k in league_avg.keys()}
        team_weakness = {k: 0.5 for k in league_avg.keys()}  # arbitrary positive weakness
        with pytest.raises(InputValidationError):
            domain.compute_value_score(
                latest_war=None,
                player_latest_stats=player_stats,
                league_avg=league_avg,
                league_std=league_std,
                team_weakness=team_weakness,
            )
