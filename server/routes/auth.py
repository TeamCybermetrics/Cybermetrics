from fastapi import APIRouter, status, Header, HTTPException, Request, Depends
from models.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from dependency.dependencies import get_auth_service
from services.auth_service import AuthService
from middleware.rate_limit import rate_limiter, rate_limit_signup, rate_limit_login
from typing import Annotated

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    client_ip: Annotated[str, Depends(rate_limit_signup)]
):
    """
    Create a new user account using the provided registration data.
    
    Rate limiting is applied by IP address via dependency injection to prevent signup spam.
    
    Parameters:
        signup_data (SignupRequest): User registration information such as email, password, and profile fields.
        auth_service (AuthService): Injected authentication service.
        client_ip (str): Client IP address from rate limiting dependency.
    
    Returns:
        SignupResponse: Details of the newly created user.
    """
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    client_ip: Annotated[str, Depends(rate_limit_login)]
):
    """
    Authenticate the user credentials while applying IP- and email-based rate limits.
    
    IP-based rate limiting is applied via dependency injection. Email-based rate limiting is checked 
    in the route handler. On successful authentication, resets the failed-attempt counters for that 
    IP and email. If authentication fails with HTTP 401, records a failed attempt for both the IP 
    and email and re-raises the original HTTPException.
    
    Parameters:
        login_data (LoginRequest): Credentials for authentication; the `email` field is used for email-based rate limiting.
        auth_service (AuthService): Injected authentication service.
        client_ip (str): Client IP address from rate limiting dependency.
    
    Returns:
        LoginResponse: Authentication result returned by the authentication service.
    
    Raises:
        fastapi.HTTPException: Propagates HTTP exceptions from the authentication service (401 responses also increment rate-limit counters).
    """
    # Check email-based rate limit (IP already checked by dependency)
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
async def verify_token(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None
):
    """
    Validate and verify a Bearer token extracted from the Authorization header.
    
    Parameters:
        auth_service (AuthService): Injected authentication service.
        authorization (str | None): The Authorization header value in the form "Bearer <token>".
    
    Returns:
        dict: The authentication service's verification result (decoded token / verification payload).
    
    Raises:
        HTTPException: 401 if authorization header is missing, malformed, or token is invalid.
    """
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
