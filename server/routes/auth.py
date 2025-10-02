from fastapi import APIRouter, status, Header, HTTPException
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_data: SignupRequest):
    """Create a new user account with Firebase Authentication"""
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and generate custom token
    Note: In production, you should use Firebase Client SDK for authentication
    This endpoint demonstrates backend validation
    """
    return await auth_service.login(login_data)

@router.get("/verify")
async def verify_token(authorization: str = Header(None)):
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

