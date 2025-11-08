from abc import ABC, abstractmethod
from typing import List, Optional
from models.free_agents import FreeAgentPlayer, StoredFreeAgent, FreeAgentsResponse


class FreeAgentsRepository(ABC):
    """Abstract interface for free agents data access"""
    
    @abstractmethod
    async def fetch_free_agents_from_api(self) -> FreeAgentsResponse:
        """Fetch free agents from Sportradar API"""
        pass
    
    @abstractmethod
    async def store_free_agent(self, agent: StoredFreeAgent) -> StoredFreeAgent:
        """Store a single free agent in Firebase"""
        pass
    
    @abstractmethod
    async def get_stored_free_agents(self) -> List[StoredFreeAgent]:
        """Get all stored free agents from Firebase"""
        pass
    
    @abstractmethod
    async def get_free_agent_by_mlbam_id(self, mlbam_id: str) -> Optional[StoredFreeAgent]:
        """Get a specific free agent by MLBAM ID from Firebase"""
        pass
    
    @abstractmethod
    async def delete_free_agent(self, mlbam_id: str) -> bool:
        """Delete a free agent from Firebase"""
        pass
    
    @abstractmethod
    async def bulk_store_free_agents(self, agents: List[StoredFreeAgent]) -> int:
        """Store multiple free agents in Firebase, returns count of stored agents"""
        pass
