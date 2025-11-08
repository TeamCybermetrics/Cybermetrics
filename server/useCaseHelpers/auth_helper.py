from fastapi import HTTPException, status
from entities.auth import LoginRequest, SignupRequest, User

class AuthDomain:
    def __init__(self):
        pass  
    
    def validate_signup_data(self, signup_data: SignupRequest) -> None:
        """Pure business logic: validate signup data"""
        if not signup_data.email or not signup_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if len(signup_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
    
    def validate_login_data(self, login_data: LoginRequest) -> None:
        """Pure business logic: validate login data"""
        if not login_data.email or not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
    
    def validate_token_format(self, token: str) -> None:
        """Pure business logic: validate token format"""
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is required"
            )
    
    def validate_user_exists(self, user: User) -> None:
        """Pure business logic: validate user exists"""
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )