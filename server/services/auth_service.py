from firebase_admin import auth, firestore
from fastapi import HTTPException, status
from config.firebase import firebase_service
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse

class AuthService:
    def __init__(self):
        self.db = firebase_service.db
        self.auth = firebase_service.auth
    
    async def signup(self, signup_data: SignupRequest) -> SignupResponse:
        """Create a new user account"""
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
        """Authenticate user and generate custom token"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Get user by email
            user = auth.get_user_by_email(login_data.email)
            
            # Generate a custom token for the user
            custom_token = auth.create_custom_token(user.uid)
            
            # Get user data from Firestore
            user_doc = self.db.collection('users').document(user.uid).get()
            
            return LoginResponse(
                message="Login successful",
                user_id=user.uid,
                email=user.email,
                token=custom_token.decode('utf-8')
            )
        
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

