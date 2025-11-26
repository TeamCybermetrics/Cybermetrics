"""
Unit tests for adjustment and value score logic in `RosterDomain`.
"""
import pytest
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.errors import InputValidationError
from useCaseHelpers.tests.value_adjustment_utils import (
    PLAYER_STATS,
    LEAGUE_AVG,
    LEAGUE_STD,
    TEAM_WEAKNESS_MIXED,
    manual_contrib,
)


class TestComputeAdjustmentSum:
    """Tests for `compute_adjustment_sum` covering direction, weighting & edge cases."""

    @pytest.fixture
    def domain(self):
        return RosterDomain()

    @pytest.mark.unit
    def test_expected_contributions(self, domain):
        adj_sum, contribs = domain.compute_adjustment_sum(
            player_latest_stats=PLAYER_STATS,
            league_avg=LEAGUE_AVG,
            league_std=LEAGUE_STD,
            team_weakness=TEAM_WEAKNESS_MIXED,
        )
        manual_sum, manual_contribs = manual_contrib(PLAYER_STATS, LEAGUE_AVG, LEAGUE_STD, TEAM_WEAKNESS_MIXED)

        assert adj_sum == pytest.approx(manual_sum)
        assert contribs["strikeout_rate"] == pytest.approx(manual_contribs["strikeout_rate"])  # league - player
        assert contribs["walk_rate"] == pytest.approx(manual_contribs["walk_rate"])  # player - league

    @pytest.mark.unit
    def test_negative_weights_uses_abs(self, domain):
        team_weakness = {"walk_rate": -1.0}
        player_stats = {"walk_rate": 0.11}
        league_avg = {"walk_rate": 0.08}
        league_std = {"walk_rate": 0.01}

        adj_sum, contribs = domain.compute_adjustment_sum(
            player_latest_stats=player_stats,
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        assert contribs["walk_rate"] == pytest.approx(3.0)
        assert adj_sum == pytest.approx(3.0)

    @pytest.mark.unit
    def test_zero_std_raises(self, domain):
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
    def test_value_score_composition(self, domain):
        latest_war = 4.2
        adj_sum, _ = domain.compute_adjustment_sum(
            player_latest_stats=PLAYER_STATS,
            league_avg=LEAGUE_AVG,
            league_std=LEAGUE_STD,
            team_weakness=TEAM_WEAKNESS_MIXED,
        )
        vs = domain.compute_value_score(
            latest_war=latest_war,
            player_latest_stats=PLAYER_STATS,
            league_avg=LEAGUE_AVG,
            league_std=LEAGUE_STD,
            team_weakness=TEAM_WEAKNESS_MIXED,
        )
        assert vs["adjustment_score"] == pytest.approx(adj_sum)
        assert vs["value_score"] == pytest.approx(round(latest_war + adj_sum, 3))
        assert set(vs["contributions"].keys()) == set(PLAYER_STATS.keys())

    @pytest.mark.unit
    def test_missing_war_raises(self, domain):
        with pytest.raises(InputValidationError):
            domain.compute_value_score(
                latest_war=None,
                player_latest_stats=PLAYER_STATS,
                league_avg=LEAGUE_AVG,
                league_std=LEAGUE_STD,
                team_weakness=TEAM_WEAKNESS_MIXED,
            )
