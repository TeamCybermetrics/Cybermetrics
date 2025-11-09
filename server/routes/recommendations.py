"""API routes for roster recommendation use cases."""

from typing import List, Annotated

import logging

from fastapi import APIRouter, Depends

from models.players import PlayerSearchResult, RosterAvgRequest
from services.recommendation_service import RecommendationService
from dependency.dependencies import get_recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

logger = logging.getLogger(__name__)


@router.post("", response_model=List[PlayerSearchResult], summary="Recommend roster upgrades")
@router.post("/", response_model=List[PlayerSearchResult], summary="Recommend roster upgrades")
async def recommend_players(
    request: RosterAvgRequest,
    recommendation_service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> List[PlayerSearchResult]:
    """Return the top recommended free-agent replacements for a roster."""
    logger.info("Received recommendation request for %d player ids", len(request.player_ids))
    return await recommendation_service.recommend_players(request.player_ids)