from firebase_admin import auth, firestore
from fastapi import HTTPException, status
from config.firebase import firebase_service
from config.settings import settings
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from utils.logger import get_logger
import httpx

logger = get_logger(__name__)

class AuthService:
    def __init__(self):
        """
        Initialize the AuthService instance by binding Firebase clients and configuration.
        
        Sets the following instance attributes:
        - db: Firestore database client used for user documents.
        - auth: Firebase Admin auth client used for user operations.
        - firebase_api_key: Firebase Web API key used for REST authentication calls.
        """
        self.db = firebase_service.db
        self.auth = firebase_service.auth
        self.firebase_api_key = settings.FIREBASE_WEB_API_KEY
    
    async def signup(self, signup_data: SignupRequest) -> SignupResponse:
        """
        Create a new Firebase user account and persist basic profile data to Firestore.
        
        Parameters:
            signup_data (SignupRequest): Request data containing `email`, `password`, and `display_name` for the new user.
        
        Returns:
            SignupResponse: Response containing a success message, the created user's UID, and email.
        
        Raises:
            HTTPException: 503 if Firebase is not configured.
            HTTPException: 400 if the provided email already exists.
            HTTPException: 500 if user creation or Firestore persistence fails with an unexpected error.
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Create user in Firebase Authentication
            user = auth.create_user(
                email=signup_data.email,
                password=signup_data.password,
                display_name=signup_data.display_name
            )
            
            # Store additional user data in Firestore
            user_ref = self.db.collection('users').document(user.uid)
            user_ref.set({
                'email': signup_data.email,
                'display_name': signup_data.display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
            })
            
            return SignupResponse(
                message="User created successfully",
                user_id=user.uid,
                email=user.email
            )
        
        except auth.EmailAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        Authenticate a user with email and password and return a Firebase custom authentication token.
        
        Performs password verification via the Firebase Authentication REST API, ensures the corresponding Firebase user exists, and returns a LoginResponse containing the generated custom token and basic user information.
        
        Returns:
        	LoginResponse: Contains message, user_id, email, and a UTF-8 decoded custom token.
        
        Raises:
        	HTTPException: With status 503 if Firebase or the Firebase Web API key is not configured.
        	HTTPException: With status 401 if the email/password are invalid or the user does not exist.
        	HTTPException: With status 500 for other unexpected errors encountered during login.
        """
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        if not self.firebase_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase Web API key is not configured"
            )
        
        try:
            # CRITICAL: Verify password using Firebase Authentication REST API
            # Firebase Admin SDK doesn't provide password verification
            async with httpx.AsyncClient(timeout=10.0) as client:  # Add timeout
                firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_api_key}"
                response = await client.post(
                    firebase_auth_url,
                    json={
                        "email": login_data.email,
                        "password": login_data.password,
                        "returnSecureToken": True
                    }
                )
                
                if response.status_code != 200:
                    # Firebase returns 400 for invalid credentials
                    # Don't reveal whether email exists - same error for both cases
                    logger.warning(f"Failed login attempt for email: {login_data.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                
                auth_data = response.json()
                uid = auth_data.get("localId")
            
            # Get user to verify account still exists in Admin SDK
            user = auth.get_user(uid)
            
            # Generate a custom token for the user
            custom_token = auth.create_custom_token(user.uid)
            
            # Get user data from Firestore
            user_doc = self.db.collection('users').document(user.uid).get()
            
            logger.info(f"Successful login for user: {user.uid} ({user.email})")
            
            return LoginResponse(
                message="Login successful",
                user_id=user.uid,
                email=user.email,
                token=custom_token.decode('utf-8')
            )
        
        except HTTPException:
            # Re-raise HTTP exceptions (including auth failures)
            raise
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )
    
    async def verify_token(self, token: str) -> dict:
        """Verify a custom token by decoding it and checking if user exists"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # For custom tokens, we need to decode and verify differently
            # Custom tokens are meant to be exchanged for ID tokens on the client
            # For backend verification, we'll decode the JWT and verify the user exists
            import jwt
            from jwt import PyJWKClient
            
            # Decode without verification first to get the uid
            decoded = jwt.decode(token, options={"verify_signature": False})
            uid = decoded.get('uid')
            
            if not uid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Verify the user still exists in Firebase
            user = auth.get_user(uid)
            
            return {
                "message": "Token is valid",
                "user_id": user.uid,
                "email": user.email
            }
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {str(e)}"
            )

auth_service = AuthService()
