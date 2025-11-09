"""API routes for roster recommendation use cases."""

from typing import List, Annotated

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from entities.players import PlayerSearchResult, RosterAvgRequest
from services.recommendation_service import RecommendationService
from dependency.dependencies import get_recommendation_service
from useCaseHelpers.errors import InputValidationError, QueryError, UseCaseError

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
    try:
        return await recommendation_service.recommend_players(request.player_ids)
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except QueryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UseCaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)