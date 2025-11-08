from fastapi import APIRouter, Depends, status

from dependency import dependencies
from domain.team_builder_domain import LineupFiltersModel, LineupMapModel, SaveLineupRequest
from middleware.auth import get_current_user
from models.team_builder import (
    DeleteLineupResponse,
    LineupFiltersPayload,
    LineupResponse,
    LineupSlotPayload,
    SaveLineupPayload,
    SavedLineup,
)
from services.team_builder_service import TeamBuilderService


router = APIRouter(prefix="/api/team-builder", tags=["team-builder"])


def _to_domain(payload: SaveLineupPayload) -> SaveLineupRequest:
    """Convert request payload to domain request model."""
    lineup_map = LineupMapModel(lineup=payload.lineup)
    filters = LineupFiltersModel(
        salary_range=payload.filters.salary_range,
        selected_positions=payload.filters.selected_positions,
    )
    return SaveLineupRequest(
        name=payload.name,
        lineup=lineup_map,
        filters=filters,
        team_score=payload.team_score,
        team_budget=payload.team_budget,
        notes=payload.notes,
        is_current=True,
    )


def _to_response(lineup_model) -> SavedLineup:
    """Convert a domain SavedLineupModel to API response."""
    if lineup_model is None:
        raise ValueError("Cannot convert empty lineup model")

    lineup_payload = {
        position: (
            LineupSlotPayload(
                player_id=slot.player_id,
                name=slot.name,
                image_url=slot.image_url,
                years_active=slot.years_active,
            )
            if slot
            else None
        )
        for position, slot in lineup_model.lineup.lineup.items()
    }

    return SavedLineup(
        id=lineup_model.id,
        name=lineup_model.name,
        lineup=lineup_payload,
        filters=LineupFiltersPayload(
            salary_range=lineup_model.filters.salary_range,
            selected_positions=list(lineup_model.filters.selected_positions),
        ),
        team_score=lineup_model.team_score,
        team_budget=lineup_model.team_budget,
        notes=lineup_model.notes,
        saved_at=lineup_model.saved_at,
        updated_at=lineup_model.updated_at,
    )


@router.get("/lineup", response_model=LineupResponse, status_code=status.HTTP_200_OK)
async def get_lineup(
    current_user: str = Depends(get_current_user),
    team_builder_service: TeamBuilderService = Depends(
        dependencies.get_team_builder_service
    ),
):
    saved_lineup = await team_builder_service.get_current_lineup(current_user)
    return (
        LineupResponse(lineup=_to_response(saved_lineup))
        if saved_lineup
        else LineupResponse(lineup=None)
    )


@router.post("/lineup", response_model=LineupResponse, status_code=status.HTTP_200_OK)
async def save_lineup(
    payload: SaveLineupPayload,
    current_user: str = Depends(get_current_user),
    team_builder_service: TeamBuilderService = Depends(
        dependencies.get_team_builder_service
    ),
):
    domain_payload = _to_domain(payload)
    saved = await team_builder_service.save_current_lineup(current_user, domain_payload)
    return LineupResponse(lineup=_to_response(saved))


@router.delete(
    "/lineup", response_model=DeleteLineupResponse, status_code=status.HTTP_200_OK
)
async def delete_lineup(
    current_user: str = Depends(get_current_user),
    team_builder_service: TeamBuilderService = Depends(
        dependencies.get_team_builder_service
    ),
):
    await team_builder_service.delete_current_lineup(current_user)
    return DeleteLineupResponse()
