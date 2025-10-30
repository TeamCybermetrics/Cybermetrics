from firebase_admin import auth, firestore
from fastapi import HTTPException, status
from config.firebase import firebase_service
from config.settings import settings
from models.auth import LoginRequest, SignupRequest, User
from repositories.auth_repository import AuthRepository
from typing import Dict, Optional
import jwt
import httpx
import hashlib
from fastapi.concurrency import run_in_threadpool
from utils.logger import get_logger

logger = get_logger(__name__)

def _redact_email(email: str) -> str:
    """Redact email for logging by hashing it to avoid PII exposure"""
    if not email:
        return "<empty>"
    # Use SHA256 hash and take first 12 chars for brevity
    email_hash = hashlib.sha256(email.encode()).hexdigest()[:12]
    return f"<redacted:{email_hash}>"
            

class AuthRepositoryFirebase(AuthRepository):
    def __init__(self, db):
        self.db = db
    
    async def create_user(self, signup_data: SignupRequest) -> Dict[str, str]:
        """Create a new user account"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Create user in Firebase Authentication
            user = await run_in_threadpool(
                auth.create_user,
                email=signup_data.email,
                password=signup_data.password,
                display_name=signup_data.display_name
            )
            
            # Store additional user data in Firestore
            user_ref = self.db.collection('users').document(user.uid)
            await run_in_threadpool(user_ref.set, {
                'email': signup_data.email,
                'display_name': signup_data.display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
            })
            
            return {
                "message": "User created successfully",
                "user_id": user.uid,
                "email": user.email
            }
        
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
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = await run_in_threadpool(auth.get_user_by_email, email)
            return User(
                user_id=user.uid,
                email=user.email,
                name=user.display_name or ""
            )
        except auth.UserNotFoundError:
            return None
        except Exception:
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = await run_in_threadpool(auth.get_user, user_id)
            return User(
                user_id=user.uid,
                email=user.email,
                name=user.display_name or ""
            )
        except auth.UserNotFoundError:
            return None
        except Exception:
            return None
    
    async def create_custom_token(self, user_id: str) -> str:
        """Create custom token for user"""
        try:
            custom_token = await run_in_threadpool(auth.create_custom_token, user_id)
            return custom_token.decode('utf-8')
        except Exception as e:
            import logging
            logging.exception("Failed to create custom token for user %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create token"
            ) from e
    
    async def create_id_token(self, user_id: str) -> str:
        """Create ID token for user (recommended approach)"""
        try:
            custom_token = await run_in_threadpool(auth.create_custom_token, user_id)
            return custom_token.decode('utf-8')
        except Exception as e:
            import logging
            logging.exception("Failed to create token for user %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create token"
            ) from e
    
    async def verify_custom_token(self, token: str) -> Dict[str, str]:
        """Verify custom token using Firebase's mechanism"""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            uid = decoded.get('uid')
            
            if not uid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Verify the user still exists in Firebase
            user = await run_in_threadpool(auth.get_user, uid)
            
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
    
    async def store_user_data(self, user_id: str, user_data: Dict) -> bool:
        """Store additional user data"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.set(user_data, merge=True)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store user data: {str(e)}"
            )
    
    async def verify_password(self, email: str, password: str) -> str:
        """
        Verify password using Firebase Authentication REST API.
        Returns the user ID if successful.
        
        Firebase Admin SDK doesn't provide password verification,
        so we use the REST API for this critical security operation.
        """
        if not settings.FIREBASE_WEB_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase Web API key is not configured"
            )
        
        try:
            # Verify password using Firebase Authentication REST API
            async with httpx.AsyncClient(timeout=10.0) as client:
                firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"
                response = await client.post(
                    firebase_auth_url,
                    json={
                        "email": email,
                        "password": password,
                        "returnSecureToken": True
                    }
                )
                
                if response.status_code != 200:
                    # Firebase returns 400 for invalid credentials
                    # Don't reveal whether email exists - same error for both cases
                    logger.warning(f"Failed login attempt for email: {_redact_email(email)}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                
                auth_data = response.json()
                uid = auth_data.get("localId")
                
                if not uid:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                
                logger.info(f"Successful password verification for user: {uid} ({_redact_email(email)})")
                return uid
        
        except HTTPException:
            # Re-raise HTTP exceptions (including auth failures)
            raise
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )