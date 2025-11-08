from repositories.free_agents_repository import FreeAgentsRepository
from models.free_agents import FreeAgentPlayer, StoredFreeAgent, FreeAgentsResponse
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import httpx
import logging


class FreeAgentsRepositorySportradar(FreeAgentsRepository):
    """Sportradar API + Firebase implementation of free agents repository"""
    
    def __init__(self, db, api_key: str, base_url: str):
        self.db = db
        self.api_key = api_key
        self.base_url = base_url
        self._logger = logging.getLogger(__name__)
    
    async def fetch_free_agents_from_api(self) -> FreeAgentsResponse:
        """Fetch free agents from Sportradar API"""
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sportradar API key is not configured"
            )
        
        url = f"{self.base_url}/league/free_agents.json"
        params = {"api_key": self.api_key}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Sportradar API key"
                    )
                elif response.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Sportradar API access forbidden - check your subscription"
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Sportradar API rate limit exceeded"
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Sportradar API error: {response.status_code}"
                    )
                
                data = response.json()
                league_data = data.get("league", {})
                
                free_agents_list = []
                for agent_data in league_data.get("free_agents", []):
                    try:
                        agent = FreeAgentPlayer(**agent_data)
                        free_agents_list.append(agent)
                    except Exception as e:
                        self._logger.warning(f"Failed to parse free agent: {e}")
                        continue
                
                return FreeAgentsResponse(
                    league_id=league_data.get("id", ""),
                    league_name=league_data.get("name", ""),
                    league_alias=league_data.get("alias", ""),
                    free_agents=free_agents_list,
                    total_count=len(free_agents_list),
                    fetched_at=datetime.utcnow().isoformat()
                )
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Sportradar API request timed out"
            )
        except httpx.RequestError as e:
            self._logger.exception("Sportradar API request failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to connect to Sportradar API: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            self._logger.exception("Unexpected error fetching free agents")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch free agents: {str(e)}"
            )
    
    async def store_free_agent(self, agent: StoredFreeAgent) -> StoredFreeAgent:
        """Store a single free agent in Firebase"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            doc_ref = self.db.collection('free_agents').document(agent.mlbam_id)
            doc_ref.set(agent.dict())
            return agent
        except Exception as e:
            self._logger.exception(f"Failed to store free agent {agent.mlbam_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store free agent: {str(e)}"
            )
    
    async def get_stored_free_agents(self) -> List[StoredFreeAgent]:
        """Get all stored free agents from Firebase"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            docs = self.db.collection('free_agents').stream()
            agents = []
            for doc in docs:
                try:
                    agent = StoredFreeAgent(**doc.to_dict())
                    agents.append(agent)
                except Exception as e:
                    self._logger.warning(f"Failed to parse stored free agent: {e}")
                    continue
            return agents
        except Exception as e:
            self._logger.exception("Failed to get stored free agents")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get stored free agents: {str(e)}"
            )
    
    async def get_free_agent_by_mlbam_id(self, mlbam_id: str) -> Optional[StoredFreeAgent]:
        """Get a specific free agent by MLBAM ID from Firebase"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            doc = self.db.collection('free_agents').document(mlbam_id).get()
            if not doc.exists:
                return None
            return StoredFreeAgent(**doc.to_dict())
        except Exception as e:
            self._logger.exception(f"Failed to get free agent {mlbam_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get free agent: {str(e)}"
            )
    
    async def delete_free_agent(self, mlbam_id: str) -> bool:
        """Delete a free agent from Firebase"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            self.db.collection('free_agents').document(mlbam_id).delete()
            return True
        except Exception as e:
            self._logger.exception(f"Failed to delete free agent {mlbam_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete free agent: {str(e)}"
            )
    
    async def bulk_store_free_agents(self, agents: List[StoredFreeAgent]) -> int:
        """Store multiple free agents in Firebase, returns count of stored agents"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            batch = self.db.batch()
            count = 0
            
            for agent in agents:
                doc_ref = self.db.collection('free_agents').document(agent.mlbam_id)
                batch.set(doc_ref, agent.dict())
                count += 1
                
                # Firestore batch limit is 500 operations
                if count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            # Commit remaining operations
            if count % 500 != 0:
                batch.commit()
            
            return count
        except Exception as e:
            self._logger.exception("Failed to bulk store free agents")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to bulk store free agents: {str(e)}"
            )
