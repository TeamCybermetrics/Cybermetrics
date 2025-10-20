from fastapi import APIRouter, status, Header, HTTPException, Depends
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse  # ← Still need models!
from dependency.dependencies import get_auth_service
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_data: SignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Create a new user account with Firebase Authentication"""
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Authenticate user and generate custom token
    Note: In production, you should use Firebase Client SDK for authentication
    This endpoint demonstrates backend validation
    """
    return await auth_service.login(login_data)

@router.get("/verify")
async def verify_token(authorization: str = Header(None), auth_service: AuthService = Depends(get_auth_service)):
    """Verify a Firebase custom token from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
    
    token = parts[1]
    return await auth_service.verify_token(token)

