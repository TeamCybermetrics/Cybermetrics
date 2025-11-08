from repositories.free_agents_repository import FreeAgentsRepository
from domain.free_agents_domain import FreeAgentsDomain
from models.free_agents import FreeAgentsResponse, StoredFreeAgent
from fastapi import HTTPException, status
from typing import List, Optional
import logging


class FreeAgentsService:
    """Service for managing free agents - pure orchestration"""
    
    def __init__(self, free_agents_repository: FreeAgentsRepository, free_agents_domain: FreeAgentsDomain):
        self.free_agents_repository = free_agents_repository
        self.free_agents_domain = free_agents_domain
        self._logger = logging.getLogger(__name__)
    
    async def fetch_and_store_free_agents(self) -> dict:
        """
        Fetch free agents from Sportradar API and store them in Firebase.
        Returns summary of operation.
        """
        # Fetch from API
        api_response = await self.free_agents_repository.fetch_free_agents_from_api()
        
        # Filter valid agents using domain logic
        valid_agents = self.free_agents_domain.filter_valid_free_agents(api_response.free_agents)
        
        if not valid_agents:
            return {
                "success": True,
                "message": "No valid free agents found",
                "fetched_count": api_response.total_count,
                "stored_count": 0,
                "updated_count": 0,
                "new_count": 0
            }
        
        # Transform and store agents
        stored_agents = []
        updated_count = 0
        new_count = 0
        
        for agent in valid_agents:
            # Transform to stored format
            stored_agent = self.free_agents_domain.transform_sportradar_to_stored(agent)
            
            # Check if agent already exists
            existing = await self.free_agents_repository.get_free_agent_by_mlbam_id(stored_agent.mlbam_id)
            
            if existing:
                # Check if we should update
                if self.free_agents_domain.should_update_agent(existing.last_updated, stored_agent.last_updated):
                    stored_agents.append(stored_agent)
                    updated_count += 1
            else:
                stored_agents.append(stored_agent)
                new_count += 1
        
        # Bulk store agents
        stored_count = 0
        if stored_agents:
            stored_count = await self.free_agents_repository.bulk_store_free_agents(stored_agents)
        
        return {
            "success": True,
            "message": f"Successfully processed {stored_count} free agents",
            "fetched_count": api_response.total_count,
            "valid_count": len(valid_agents),
            "stored_count": stored_count,
            "updated_count": updated_count,
            "new_count": new_count,
            "fetched_at": api_response.fetched_at
        }
    
    async def get_all_free_agents(self) -> List[StoredFreeAgent]:
        """Get all stored free agents from database"""
        return await self.free_agents_repository.get_stored_free_agents()
    
    async def get_free_agent_by_mlbam_id(self, mlbam_id: str) -> StoredFreeAgent:
        """Get a specific free agent by MLBAM ID"""
        agent = await self.free_agents_repository.get_free_agent_by_mlbam_id(mlbam_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Free agent with MLBAM ID {mlbam_id} not found"
            )
        
        return agent
    
    async def refresh_free_agents(self) -> dict:
        """
        Refresh free agents list by fetching latest from API.
        This is an alias for fetch_and_store_free_agents for clarity.
        """
        return await self.fetch_and_store_free_agents()
