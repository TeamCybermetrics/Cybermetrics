import pytest
from services.roster_avg_service import RosterAvgService
from services.tests.mocks.mock_repositories import MockRosterRepository
from services.tests.mocks.repository_test_utils import build_fake_players
from useCaseHelpers.roster_helper import RosterDomain
from services.tests.mocks.mock_repositories import MockPlayerRepository
from useCaseHelpers.errors import InputValidationError


class TestRosterAvgServiceWeakness:
    @pytest.fixture
    def service(self):
        roster_repo = MockRosterRepository()
        player_repo = MockPlayerRepository()
        domain = RosterDomain()
        return roster_repo, player_repo, domain

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_matches_domain(self, service):
        roster_repo, player_repo, domain = service
        players = build_fake_players()
        for pid, seasons in players.items():
            roster_repo.set_players_seasons_data(pid, seasons)
        svc = RosterAvgService(roster_repo, domain, player_repo)
        player_ids = list(players.keys())
        result = await svc.get_team_weakness_scores(player_ids)
        players_data = await roster_repo.get_players_seasons_data(player_ids)
        roster_resp = domain.calculate_roster_averages(players_data)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        league_avg = await roster_repo.get_league_unweighted_average()
        league_std = await roster_repo.get_league_unweighted_std()
        expected = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        assert result == pytest.approx(expected)
        assert set(result.keys()) == set(expected.keys())

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_empty_ids_raises(self, service):
        roster_repo, player_repo, domain = service
        svc = RosterAvgService(roster_repo, domain, player_repo)
        with pytest.raises(InputValidationError):
            await svc.get_team_weakness_scores([])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_with_explicit_league_vectors(self, service):
        roster_repo, player_repo, domain = service
        players = build_fake_players()
        for pid, seasons in players.items():
            roster_repo.set_players_seasons_data(pid, seasons)
        roster_repo.set_league_avg({
            "strikeout_rate": 0.22,
            "walk_rate": 0.09,
            "isolated_power": 0.17,
            "on_base_percentage": 0.320,
            "base_running": 1.8,
        })
        roster_repo.set_league_std({
            "strikeout_rate": 0.02,
            "walk_rate": 0.01,
            "isolated_power": 0.025,
            "on_base_percentage": 0.012,
            "base_running": 0.4,
        })
        svc = RosterAvgService(roster_repo, domain, player_repo)
        player_ids = list(players.keys())
        result = await svc.get_team_weakness_scores(player_ids)
        players_data = await roster_repo.get_players_seasons_data(player_ids)
        roster_resp = domain.calculate_roster_averages(players_data)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        expected = domain.compute_team_weakness_scores(team_avg, roster_repo._league_avg, roster_repo._league_std)
        assert result == pytest.approx(expected)
        for v in result.values():
            assert isinstance(v, float)
