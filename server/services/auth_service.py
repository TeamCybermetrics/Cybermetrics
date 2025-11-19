from useCaseHelpers.auth_helper import AuthDomain
from repositories.auth_repository import AuthRepository
from dtos.auth_dtos import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from useCaseHelpers.errors import InputValidationError, AuthError, DatabaseError, DependencyUnavailableError


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
            InputValidationError: if validation fails or email already exists.
            DatabaseError: if user creation fails unexpectedly.
        """
        try:
            self.auth_domain.validate_signup_data(signup_data)
            result = await self.auth_repository.create_user(signup_data)
        except InputValidationError:
            raise
        except Exception as e:
            raise DatabaseError("Failed to create user") from e
        
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
            InputValidationError: invalid login input.
            AuthError: invalid credentials or user not found.
            DependencyUnavailableError: Firebase API key not configured.
            DatabaseError: unexpected error during login.
        """
        try:
            self.auth_domain.validate_login_data(login_data)
            user_id = await self.auth_repository.verify_password(login_data.email, login_data.password)
            user = await self.auth_repository.get_user_by_id(user_id)
            self.auth_domain.validate_user_exists(user)
            token = await self.auth_repository.create_custom_token(user.user_id)
        except InputValidationError:
            raise
        except AuthError:
            raise
        except KeyError:
            raise DependencyUnavailableError("Firebase API key not configured")
        except Exception as e:
            raise DatabaseError("Login failed unexpectedly") from e
        
        return LoginResponse(
            message="Login successful",
            user_id=user.user_id,
            email=user.email,
            token=token,
            display_name=user.name
        )
    
    async def verify_token(self, token: str) -> dict:
        """
        Validate and verify a Bearer token.
        
        Parameters:
            token (str): The authentication token to verify.
        
        Returns:
            dict: The authentication service's verification result (decoded token / verification payload).
        
        Raises:
            AuthError: token invalid, expired, or user not found.
        """
        try:
            self.auth_domain.validate_token_format(token)
            result = await self.auth_repository.verify_custom_token(token)
            return result
        except AuthError:
            raise
        except Exception as e:
            raise AuthError("Token verification failed") from e
