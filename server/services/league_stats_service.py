from typing import List
from entities.league_stats import TeamAggregate, LeagueAggregate
from useCaseHelpers.league_stats_helper import LeagueStatsDomain
from repositories.player_repository import PlayerRepository
import logging

logger = logging.getLogger(__name__)


class LeagueStatsService:
    def __init__(self, player_repository: PlayerRepository, domain: LeagueStatsDomain):
        self.player_repository = player_repository
        self.domain = domain

    def persist_league_aggregate(self, aggregate: LeagueAggregate) -> None:
        self.player_repository.set_league_averages(aggregate.model_dump())

    def build_team_aggregate(self, team_id: str, avg: dict, player_count: int) -> TeamAggregate:
        return TeamAggregate(team_id=team_id, avg=avg, player_count=player_count)

    def compute_and_persist(self, team_aggregates: List[TeamAggregate]) -> LeagueAggregate:
        aggregate = self.domain.compute_league_aggregate(team_aggregates)
        try:
            self.persist_league_aggregate(aggregate)
        except Exception:
            logger.exception("Failed to persist league aggregate")
            raise
        return aggregate
