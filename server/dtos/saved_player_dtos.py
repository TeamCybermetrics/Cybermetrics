from pydantic import BaseModel
from typing import Optional

# ============================================================================
# INPUT DTOs (Requests)
# ============================================================================

class UpdateSavedPlayerPositionRequest(BaseModel):
    """
    Request to update a saved player's lineup position.
    
    Allows users to organize their saved players by
    assigning them to specific lineup positions.
    """
    position: Optional[str] = None


# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class AddPlayerResponse(BaseModel):
    """
    Response returned after successfully adding a player.
    
    Confirms the player was added and provides the player ID.
    """
    message: str
    player_id: str

class DeletePlayerResponse(BaseModel):
    """
    Response returned after successfully deleting a player.
    
    Confirms the player was removed from saved players.
    """
    message: str
