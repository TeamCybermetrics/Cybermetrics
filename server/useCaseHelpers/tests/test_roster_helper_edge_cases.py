import pytest
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.errors import InputValidationError


class TestRosterHelperEdgeCases:
    @pytest.fixture
    def domain(self):
        return RosterDomain()

    def test_validate_player_ids_empty_raises(self, domain):
        with pytest.raises(InputValidationError):
            domain.validate_player_ids([])

    def test_calculate_player_averages_empty_seasons(self, domain):
        assert domain.calculate_player_averages({}) is None

    def test_calculate_player_averages_all_zero_pa(self, domain):
        seasons = {
            "2022": {"plate_appearances": 0, "strikeout_rate": 0.25},
            "2023": {"plate_appearances": 0, "walk_rate": 0.10},
        }
        assert domain.calculate_player_averages(seasons) is None

    def test_compute_unweighted_roster_average_empty_list_raises(self, domain):
        with pytest.raises(InputValidationError):
            domain.compute_unweighted_roster_average_dict([])

    def test_compute_unweighted_roster_average_all_none_raises(self, domain):
        with pytest.raises(InputValidationError):
            domain.compute_unweighted_roster_average_dict([None, None])

    def test_calculate_player_latest_war_no_pa(self, domain):
        seasons = {
            "2022": {"plate_appearances": 0, "war": 1.2},
            "2023": {"plate_appearances": 0, "war": 2.5},
        }
        assert domain.calculate_player_latest_war(seasons) is None

    def test_calculate_player_latest_war_non_int_year_keys(self, domain):
        seasons = {
            "Y22": {"plate_appearances": 120, "war": 1.2},
            "Y23": {"plate_appearances": 150, "war": 2.5},
        }
        result = domain.calculate_player_latest_war(seasons)
        assert result == pytest.approx(2.5)

    def test_get_player_latest_stats_fallback_no_pa(self, domain):
        seasons = {
            "2023": {"plate_appearances": 0, "strikeout_rate": 0.22, "walk_rate": 0.08,
                      "isolated_power": 0.18, "on_base_percentage": 0.330, "base_running": 1.5},
            "2022": {"plate_appearances": 0, "strikeout_rate": 0.24, "walk_rate": 0.07,
                      "isolated_power": 0.15, "on_base_percentage": 0.310, "base_running": 1.0},
        }
        stats = domain.get_player_latest_stats(seasons)
        assert stats["strikeout_rate"] == pytest.approx(0.22)
        assert stats["isolated_power"] == pytest.approx(0.18)

    def test_compute_value_score_empty_stats_defaults(self, domain):
        league_avg = {"strikeout_rate": 0.23, "walk_rate": 0.09, "isolated_power": 0.17,
                      "on_base_percentage": 0.320, "base_running": 2.0}
        league_std = {"strikeout_rate": 0.02, "walk_rate": 0.01, "isolated_power": 0.03,
                      "on_base_percentage": 0.015, "base_running": 0.5}
        team_weakness = {k: 0.5 for k in league_avg.keys()}
        result = domain.compute_value_score(
            latest_war=1.5,
            player_latest_stats={},
            league_avg=league_avg,
            league_std=league_std,
            team_weakness=team_weakness,
        )
        assert result["latest_war"] == 1.5
        assert set(result["contributions"].keys()) == set(league_avg.keys())
        assert result["contributions"]["walk_rate"] < 0
        assert result["contributions"]["strikeout_rate"] > 0
