from pydantic import BaseModel
from typing import Optional

# ============================================================================
# INPUT DTOs (Requests)
# ============================================================================

class UpdateSavedPlayerPositionRequest(BaseModel):
    """DTO: Payload for updating a saved player's lineup position"""
    position: Optional[str] = None


# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class AddPlayerResponse(BaseModel):
    """DTO: Response after adding a player"""
    message: str
    player_id: str

class DeletePlayerResponse(BaseModel):
    """DTO: Response after deleting a player"""
    message: str
