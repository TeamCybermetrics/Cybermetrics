from domain.auth_domain import AuthDomain
from repositories.auth_repository import AuthRepository
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse


class AuthService:
    def __init__(self, auth_repository: AuthRepository, auth_domain: AuthDomain):
        self.auth_repository = auth_repository
        self.auth_domain = auth_domain
    
    async def signup(self, signup_data: SignupRequest) -> SignupResponse:
        """Use Case: Create a new user account"""
        # Call domain for business logic validation
        self.auth_domain.validate_signup_data(signup_data)
        
        # repository interface
        result = await self.auth_repository.create_user(signup_data)
        
        return SignupResponse(
            message=result["message"],
            user_id=result["user_id"],
            email=result["email"]
        )
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Use Case: Authenticate user"""
        # Call domain for business logic validation
        self.auth_domain.validate_login_data(login_data)
        
        # repository interface
        user = await self.auth_repository.get_user_by_email(login_data.email)
        
        # domain for business logic validation
        self.auth_domain.validate_user_exists(user)
        
        # repository interface
        token = await self.auth_repository.create_custom_token(user.user_id)
        
        return LoginResponse(
            message="Login successful",
            user_id=user.user_id,
            email=user.email,
            token=token
        )
    
    async def verify_token(self, token: str) -> dict:
        """Use Case: Verify token"""
        # domain layer validating token
        self.auth_domain.validate_token_format(token)
        
        # repository interface
        result = await self.auth_repository.verify_custom_token(token)
        
        return result