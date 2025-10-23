from fastapi import APIRouter, status, Header, HTTPException, Request
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from services.auth_service import auth_service
from middleware.rate_limit import rate_limiter, get_client_ip

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_data: SignupRequest, request: Request):
    """Create a new user account with Firebase Authentication"""
    # Rate limit by IP to prevent signup spam
    client_ip = await get_client_ip(request)
    await rate_limiter.check_rate_limit(f"signup:{client_ip}")
    
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, request: Request):
    """
    Authenticate user and generate custom token
    Note: In production, you should use Firebase Client SDK for authentication
    This endpoint demonstrates backend validation with security enhancements
    """
    # Get client IP for rate limiting
    client_ip = await get_client_ip(request)
    
    # Check rate limits BEFORE attempting login (prevent DoS)
    await rate_limiter.check_rate_limit(f"login:ip:{client_ip}")
    await rate_limiter.check_rate_limit(f"login:email:{login_data.email}")
    
    try:
        # Attempt login
        result = await auth_service.login(login_data)
        
        # Login succeeded - reset failed attempt counters
        await rate_limiter.reset_attempts(f"login:ip:{client_ip}")
        await rate_limiter.reset_attempts(f"login:email:{login_data.email}")
        
        return result
        
    except HTTPException as e:
        # Login failed - record the failed attempt
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            await rate_limiter.record_failed_attempt(f"login:ip:{client_ip}")
            await rate_limiter.record_failed_attempt(f"login:email:{login_data.email}")
        
        # Re-raise the exception
        raise

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

