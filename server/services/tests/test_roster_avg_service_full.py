import pytest
from services.roster_avg_service import RosterAvgService
from services.tests.mocks.mock_repositories import MockRosterRepository, MockPlayerRepository
from useCaseHelpers.roster_helper import RosterDomain
from useCaseHelpers.errors import InputValidationError, QueryError, UseCaseError


def _season(war: float, pa: int = 100, k: float = 0.20, bb: float = 0.10, iso: float = 0.150,
           obp: float = 0.330, bsr: float = 1.5):
    return {
        "plate_appearances": pa,
        "war": war,
        "strikeout_rate": k,
        "walk_rate": bb,
        "isolated_power": iso,
        "on_base_percentage": obp,
        "base_running": bsr,
    }


class TestRosterAvgServiceFull:
    @pytest.fixture
    def setup(self):
        roster_repo = MockRosterRepository()
        player_repo = MockPlayerRepository()
        domain = RosterDomain()
        service = RosterAvgService(roster_repo, domain, player_repo)
        return service, roster_repo, player_repo, domain

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_success(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(1, {"2023": _season(3.2)})
        roster_repo.set_players_seasons_data(2, {"2023": _season(1.1)})
        resp = await service.get_roster_averages([1, 2])
        assert resp.total_players == 2
        assert 1 in resp.stats and 2 in resp.stats

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_roster_averages_empty_ids_raises(self, setup):
        service, roster_repo, player_repo, domain = setup
        with pytest.raises(InputValidationError):
            await service.get_roster_averages([])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_unweighted_roster_average_success(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(5, {"2023": _season(2.0, k=0.21, bb=0.11)})
        roster_repo.set_players_seasons_data(6, {"2023": _season(1.5, k=0.19, bb=0.09)})
        avg = await service.get_unweighted_roster_average([5, 6])
        assert "strikeout_rate" in avg and "walk_rate" in avg
        assert avg["strikeout_rate"] == pytest.approx(0.20)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_success(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(7, {"2023": _season(2.0, k=0.22, bb=0.09)})
        roster_repo.set_players_seasons_data(8, {"2023": _season(3.1, k=0.24, bb=0.08)})
        scores = await service.get_team_weakness_scores([7, 8])
        assert set(scores.keys()) == {"strikeout_rate","walk_rate","isolated_power","on_base_percentage","base_running"}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_matches_domain(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(10, {"2023": _season(2.5, k=0.21, bb=0.11)})
        roster_repo.set_players_seasons_data(11, {"2023": _season(3.0, k=0.23, bb=0.09)})
        roster_repo.set_players_seasons_data(12, {"2023": _season(1.7, k=0.25, bb=0.08)})
        ids = [10,11,12]
        result = await service.get_team_weakness_scores(ids)
        players_data = await roster_repo.get_players_seasons_data(ids)
        roster_resp = domain.calculate_roster_averages(players_data)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        league_avg = await roster_repo.get_league_unweighted_average()
        league_std = await roster_repo.get_league_unweighted_std()
        expected = domain.compute_team_weakness_scores(team_avg, league_avg, league_std)
        assert result == pytest.approx(expected)
        assert set(result.keys()) == set(expected.keys())

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_weakness_scores_with_explicit_league_vectors(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(13, {"2023": _season(2.2, k=0.22, bb=0.09)})
        roster_repo.set_players_seasons_data(14, {"2023": _season(3.4, k=0.24, bb=0.08)})
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
        ids = [13,14]
        result = await service.get_team_weakness_scores(ids)
        players_data = await roster_repo.get_players_seasons_data(ids)
        roster_resp = domain.calculate_roster_averages(players_data)
        team_avg = domain.compute_unweighted_roster_average_dict(list(roster_resp.stats.values()))
        expected = domain.compute_team_weakness_scores(team_avg, roster_repo._league_avg, roster_repo._league_std)
        assert result == pytest.approx(expected)
        for v in result.values():
            assert isinstance(v, float)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_value_score_success(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(9, {"2024": _season(4.4, k=0.23, bb=0.12, iso=0.200, obp=0.360, bsr=2.0)})
        roster_repo.set_league_avg({"strikeout_rate":0.22,"walk_rate":0.09,"isolated_power":0.180,"on_base_percentage":0.340,"base_running":1.7})
        roster_repo.set_league_std({"strikeout_rate":0.02,"walk_rate":0.01,"isolated_power":0.03,"on_base_percentage":0.015,"base_running":0.5})
        player_repo.add_player({"mlbam_id":9,"name":"Nine"})
        weakness = await service.get_team_weakness_scores([9])
        vs = await service.get_value_score(9, weakness)
        assert "value_score" in vs and "adjustment_score" in vs
        assert vs["latest_war"] == pytest.approx(4.4)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_value_score_player_not_found(self, setup):
        service, roster_repo, player_repo, domain = setup
        with pytest.raises(QueryError):
            await service.get_value_score(999, {})

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_mixed_outcomes(self, setup):
        service, roster_repo, player_repo, domain = setup
        roster_repo.set_players_seasons_data(1, {"2023": _season(1.1, k=0.21, bb=0.10)})
        player_repo.add_player({"mlbam_id":1, "name":"P1"})
        roster_repo.set_players_seasons_data(2, {"2023": _season(2.2, k=0.22, bb=0.11)})
        player_repo.add_player({"mlbam_id":2, "name":"P2"})
        roster_repo.set_players_seasons_data(3, {"2023": _season(3.3, k=0.23, bb=0.09)})
        player_repo.add_player({"mlbam_id":3, "name":"P3"})
        roster_repo.set_players_seasons_data(4, {"2023": _season(4.4, k=0.24, bb=0.08)})

        original_compute = domain.compute_value_score

        def fake_compute(latest_war, player_latest_stats, league_avg, league_std, team_weakness):
            if latest_war == 2.2:
                raise UseCaseError("domain issue")
            if latest_war == 3.3:
                raise RuntimeError("unexpected")
            return original_compute(latest_war, player_latest_stats, league_avg, league_std, team_weakness)

        domain.compute_value_score = fake_compute  # monkeypatch
        results = await service.get_team_value_scores([1,2,3,4])
        assert len(results) == 1
        assert results[0].id == 1
        assert results[0].name == "P1"
        domain.compute_value_score = original_compute

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_team_value_scores_empty_ids_raises(self, setup):
        service, roster_repo, player_repo, domain = setup
        with pytest.raises(InputValidationError):
            await service.get_team_value_scores([])

