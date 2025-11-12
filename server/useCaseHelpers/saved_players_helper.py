from .errors import InputValidationError

class SavedPlayersDomain:
    def __init__(self):
        pass  
    
    def validate_player_info(self, player_info: dict) -> str:
        """Validates the information of the players and return the id if they have it"""
        player_id = self.validate_player_id(player_info.get("id"))
        player_info["position"] = self.normalize_position(player_info.get("position"))
        return player_id

    def validate_player_id(self, player_id: object) -> str:
        if player_id is None:
            raise InputValidationError("Player ID is required")
        player_id_str = str(player_id).strip()
        if not player_id_str:
            raise InputValidationError("Player ID is required")
        return player_id_str

    def normalize_position(self, position: object) -> str | None:
        if position is None:
            return None
        if not isinstance(position, str):
            raise InputValidationError("Position must be a string")
        normalized = position.strip().upper()
        if not normalized:
            return None
        return normalized

        