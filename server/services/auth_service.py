from domain.auth_domain import AuthDomain
from repositories.auth_repository import AuthRepository
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse


class AuthService:
    def __init__(self, auth_repository: AuthRepository, auth_domain: AuthDomain):
        """
        Initialize the AuthService with repository and domain layers.
        
        Parameters:
            auth_repository: Repository for Firebase authentication operations
            auth_domain: Domain layer for business logic validation
        """
        self.auth_repository = auth_repository
        self.auth_domain = auth_domain
    
    async def signup(self, signup_data: SignupRequest) -> SignupResponse:
        """
        Create a new Firebase user account and persist basic profile data to Firestore.
        
        Parameters:
            signup_data (SignupRequest): Request data containing `email`, `password`, and `display_name` for the new user.
        
        Returns:
            SignupResponse: Response containing a success message, the created user's UID, and email.
        
        Raises:
            HTTPException: 400 if validation fails or email already exists.
            HTTPException: 500 if user creation fails with an unexpected error.
        """
        # Call domain for business logic validation
        self.auth_domain.validate_signup_data(signup_data)
        
        # Repository interface - create user
        result = await self.auth_repository.create_user(signup_data)
        
        return SignupResponse(
            message=result["message"],
            user_id=result["user_id"],
            email=result["email"]
        )
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        Authenticate a user with email and password and return a Firebase custom authentication token.
        
        Performs password verification via the Firebase Authentication REST API, ensures the corresponding 
        Firebase user exists, and returns a LoginResponse containing the generated custom token and basic 
        user information.
        
        Parameters:
            login_data (LoginRequest): Credentials for authentication containing email and password.
        
        Returns:
            LoginResponse: Contains message, user_id, email, and a UTF-8 decoded custom token.
        
        Raises:
            HTTPException: 503 if Firebase Web API key is not configured.
            HTTPException: 401 if the email/password are invalid or the user does not exist.
            HTTPException: 500 for other unexpected errors encountered during login.
        """
        # Call domain for business logic validation
        self.auth_domain.validate_login_data(login_data)
        
        # CRITICAL: Verify password using Firebase Authentication REST API
        # Firebase Admin SDK doesn't provide password verification
        user_id = await self.auth_repository.verify_password(login_data.email, login_data.password)
        
        # Get user details to verify account still exists
        user = await self.auth_repository.get_user_by_id(user_id)
        
        # Domain validation - ensure user exists
        self.auth_domain.validate_user_exists(user)
        
        # Create custom token for the authenticated user
        token = await self.auth_repository.create_custom_token(user.user_id)
        
        return LoginResponse(
            message="Login successful",
            user_id=user.user_id,
            email=user.email,
            token=token
        )
    
    async def verify_token(self, token: str) -> dict:
        """
        Validate and verify a Bearer token.
        
        Parameters:
            token (str): The authentication token to verify.
        
        Returns:
            dict: The authentication service's verification result (decoded token / verification payload).
        
        Raises:
            HTTPException: 401 if token is invalid, expired, or user not found.
        """
        # Domain layer validating token format
        self.auth_domain.validate_token_format(token)
        
        # Repository interface - verify token
        result = await self.auth_repository.verify_custom_token(token)
        
        return result
