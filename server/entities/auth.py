from pydantic import BaseModel

class User(BaseModel):
    """Domain entity representing a user in the system"""
    user_id: str
    email: str
    name: str

