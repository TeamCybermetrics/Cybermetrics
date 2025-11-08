from fastapi import HTTPException, status
from typing import Dict, List
from models.free_agents import FreeAgentPlayer, StoredFreeAgent
from datetime import datetime


class FreeAgentsDomain:
    """Pure business logic for free agents"""
    
    def __init__(self):
        pass
    
    def validate_free_agent_data(self, agent_data: Dict) -> None:
        """Validate free agent data business rules"""
        if not agent_data.get("mlbam_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free agent must have a valid MLBAM ID"
            )
        
        if not agent_data.get("full_name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free agent must have a full name"
            )
    
    def transform_sportradar_to_stored(self, sportradar_agent: FreeAgentPlayer) -> StoredFreeAgent:
        """Transform Sportradar API response to stored format"""
        return StoredFreeAgent(
            mlbam_id=sportradar_agent.mlbam_id,
            sportradar_id=sportradar_agent.id,
            full_name=sportradar_agent.full_name,
            first_name=sportradar_agent.first_name,
            last_name=sportradar_agent.last_name,
            preferred_name=sportradar_agent.preferred_name,
            position=sportradar_agent.position,
            status=sportradar_agent.status,
            height=sportradar_agent.height,
            weight=sportradar_agent.weight,
            throw_hand=sportradar_agent.throw_hand,
            bat_hand=sportradar_agent.bat_hand,
            last_updated=sportradar_agent.updated,
            stored_at=datetime.utcnow().isoformat()
        )
    
    def filter_valid_free_agents(self, agents: List[FreeAgentPlayer]) -> List[FreeAgentPlayer]:
        """Filter out invalid free agents based on business rules"""
        valid_agents = []
        
        for agent in agents:
            # Only include agents with valid MLBAM IDs and names
            if agent.mlbam_id and agent.full_name and agent.status == "FA":
                valid_agents.append(agent)
        
        return valid_agents
    
    def should_update_agent(self, existing_updated: str, new_updated: str) -> bool:
        """Determine if an existing free agent should be updated"""
        try:
            # Parse ISO format timestamps
            existing_dt = datetime.fromisoformat(existing_updated.replace("+00:00", ""))
            new_dt = datetime.fromisoformat(new_updated.replace("+00:00", ""))
            
            # Update if new data is more recent
            return new_dt > existing_dt
        except Exception:
            # If parsing fails, default to updating
            return True
