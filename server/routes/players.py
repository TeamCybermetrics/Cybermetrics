from fastapi import APIRouter, Query, status, Depends, UploadFile, File, HTTPException
from models.players import (
    PlayerSearchResult, 
    AddPlayerResponse, 
    DeletePlayerResponse, 
    SavedPlayer, 
    PlayerDetail,
    RosterAvgRequest,
    RosterAvgResponse,
    ImportPlayersResponse,
    ImportPlayerError
)
from middleware.auth import get_current_user
from typing import List, Annotated, Dict
import csv
import io

from dependency.dependencies import (
    get_player_search_service, 
    get_roster_avg_service, 
    get_saved_players_service
)

# player search
from services.player_search_service import PlayerSearchService
# roster average
from services.roster_avg_service import RosterAvgService
# player save
from services.saved_players_service import SavedPlayersService


router = APIRouter(prefix="/api/players", tags=["players"])

ALLOWED_CSV_CONTENT_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/csv",
    "text/plain"
}


@router.get("/search", response_model=List[PlayerSearchResult], tags=["search"])
async def search_players(
    q: Annotated[str, Query(description="Search query for player name")], 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Search for players by name using fuzzy matching (public - no auth required)"""
    return await player_service.search(q)


@router.post("/saved", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED, tags=["saved"])
async def add_saved_player(
    player_info: dict, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Add a player to the current user's saved players collection"""
    return await saved_players_service.add_player(current_user, player_info)


@router.get("/saved", response_model=List[SavedPlayer], tags=["saved"])
async def get_saved_players(
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get all saved players for the current user"""
    return await saved_players_service.get_all_players(current_user)


@router.get("/saved/{player_id}", response_model=SavedPlayer, tags=["saved"])
async def get_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)], 
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Get a specific saved player for the current user"""
    return await saved_players_service.get_player(current_user, player_id)


@router.delete("/saved/{player_id}", response_model=DeletePlayerResponse, tags=["saved"])
async def delete_saved_player(
    player_id: str, 
    current_user: Annotated[str, Depends(get_current_user)],
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)]
):
    """Delete a player from the current user's saved players collection"""
    return await saved_players_service.delete_player(current_user, player_id)


@router.post("/saved/import", response_model=ImportPlayersResponse, tags=["saved"])
async def import_saved_players(
    current_user: Annotated[str, Depends(get_current_user)],
    saved_players_service: Annotated[SavedPlayersService, Depends(get_saved_players_service)],
    file: UploadFile = File(..., description="CSV file containing player data")
):
    """Import saved players for the current user from a CSV upload"""

    if file.content_type not in ALLOWED_CSV_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a CSV file."
        )

    raw_content = await file.read()
    if not raw_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    try:
        text_content = raw_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text_content = raw_content.decode("latin-1")

    csv_stream = io.StringIO(text_content)
    reader = csv.DictReader(csv_stream)

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV is missing a header row"
        )

    header_map: Dict[str, str] = {
        header.lower().strip(): header for header in reader.fieldnames if header
    }

    required_headers = {"id", "name"}
    missing_headers = [field for field in required_headers if field not in header_map]
    if missing_headers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV missing required columns: {', '.join(missing_headers)}"
        )

    canonical_keys = {
        "id": "id",
        "player id": "id",
        "name": "name",
        "player name": "name",
        "image_url": "image_url",
        "image url": "image_url",
        "image": "image_url",
        "years_active": "years_active",
        "years active": "years_active"
    }

    rows_to_import = []
    skipped: List[ImportPlayerError] = []

    for row_index, row in enumerate(reader, start=2):
        if row is None:
            continue

        normalized_row = {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}

        if not any(normalized_row.values()):
            continue

        player_payload: Dict[str, object] = {}

        for key, value in normalized_row.items():
            if value in (None, ""):
                continue

            normalized_key = key.lower().strip()
            canonical_key = canonical_keys.get(normalized_key)
            if canonical_key:
                player_payload[canonical_key] = value
            else:
                player_payload[key] = value

        if "id" not in player_payload or "name" not in player_payload:
            skipped.append(ImportPlayerError(row=row_index, reason="Missing required id or name column"))
            continue

        try:
            player_payload["id"] = int(float(player_payload["id"]))
        except (ValueError, TypeError):
            skipped.append(ImportPlayerError(row=row_index, reason="Player id must be numeric", player_id=str(player_payload.get("id"))))
            continue

        rows_to_import.append((row_index, player_payload))

    service_result = await saved_players_service.import_players(current_user, rows_to_import)

    combined_skipped = skipped + service_result.skipped

    return ImportPlayersResponse(
        message=service_result.message,
        imported=service_result.imported,
        total_rows=len(rows_to_import) + len(skipped),
        skipped=combined_skipped
    )


@router.post("/roster-averages", response_model=RosterAvgResponse, tags=["stats"])
async def get_roster_averages(
    request: RosterAvgRequest, 
    roster_avg_service: Annotated[RosterAvgService, Depends(get_roster_avg_service)]
):
    """Get career average statistics for multiple players"""
    return await roster_avg_service.get_roster_averages(request.player_ids)


@router.get("/{player_id}/detail", response_model=PlayerDetail, tags=["search"])
async def get_player_detail(
    player_id: int, 
    player_service: Annotated[PlayerSearchService, Depends(get_player_search_service)]
):
    """Get detailed information for a specific player (public - no auth required)"""
    return await player_service.get_player_detail(player_id)