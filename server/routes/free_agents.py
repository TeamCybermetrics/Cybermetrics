from fastapi import APIRouter, status, Depends
from models.free_agents import StoredFreeAgent
from services.free_agents_service import FreeAgentsService
from dependency.dependencies import get_free_agents_service
from typing import List

router = APIRouter(prefix="/api/free-agents", tags=["free-agents"])


@router.post("/fetch", status_code=status.HTTP_200_OK)
async def fetch_and_store_free_agents(
    free_agents_service: FreeAgentsService = Depends(get_free_agents_service)
):
    """
    Fetch free agents from Sportradar API and store them in the database.
    This endpoint will fetch the latest free agents list and update the database.
    """
    return await free_agents_service.fetch_and_store_free_agents()


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_free_agents(
    free_agents_service: FreeAgentsService = Depends(get_free_agents_service)
):
    """
    Refresh the free agents list by fetching latest data from Sportradar API.
    Alias for fetch endpoint for clarity.
    """
    return await free_agents_service.refresh_free_agents()


@router.get("/", response_model=List[StoredFreeAgent])
async def get_all_free_agents(
    free_agents_service: FreeAgentsService = Depends(get_free_agents_service)
):
    """
    Get all stored free agents from the database.
    """
    return await free_agents_service.get_all_free_agents()


@router.get("/{mlbam_id}", response_model=StoredFreeAgent)
async def get_free_agent_by_id(
    mlbam_id: str,
    free_agents_service: FreeAgentsService = Depends(get_free_agents_service)
):
    """
    Get a specific free agent by their MLBAM ID.
    """
    return await free_agents_service.get_free_agent_by_mlbam_id(mlbam_id)
