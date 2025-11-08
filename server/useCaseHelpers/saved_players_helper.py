from fastapi import HTTPException, status

class SavedPlayersDomain:
    def __init__(self):
        pass  
    
    def validate_player_info(self, player_info: dict) -> str:
        """Validates the information of the players and return the id if they have it"""
        id = player_info.get("id")
        if id is None or (isinstance(id, str) and not id.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player ID is required"
            )
        player_id = str(id).strip()
        if not player_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player ID is required"
            )
        return player_id

        