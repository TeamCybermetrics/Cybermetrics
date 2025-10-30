from abc import ABC, abstractmethod
from typing import Dict, Optional
from models.auth import LoginRequest, SignupRequest, User

class AuthRepository(ABC):
    @abstractmethod
    async def create_user(self, signup_data: SignupRequest) -> Dict[str, str]:
        """Create a new user account"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def create_custom_token(self, user_id: str) -> str:
        """Create custom token for user"""
        pass
    
    @abstractmethod
    async def verify_custom_token(self, token: str) -> Dict[str, str]:
        """Verify custom token"""
        pass
    
    @abstractmethod
    async def store_user_data(self, user_id: str, user_data: Dict) -> bool:
        """Store additional user data"""
        pass
    
    @abstractmethod
    async def verify_password(self, email: str, password: str) -> str:
        """Verify user password and return user ID if valid"""
        pass