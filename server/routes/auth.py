from fastapi import APIRouter, status, Header, HTTPException, Depends
from entities.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from dependency.dependencies import get_auth_service
from services.auth_service import AuthService
from typing import Annotated

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Create a new user account using the provided registration data.
    
    Rate limiting is automatically applied by middleware to prevent signup spam.
    
    Parameters:
        signup_data (SignupRequest): User registration information such as email, password, and profile fields.
        auth_service (AuthService): Injected authentication service.
    
    Returns:
        SignupResponse: Details of the newly created user.
    """
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Authenticate the user credentials.
    
    Rate limiting (IP and email-based) is automatically applied by middleware. Success/failure 
    tracking is also handled by middleware based on response status codes.
    
    Parameters:
        login_data (LoginRequest): Credentials for authentication.
        auth_service (AuthService): Injected authentication service.
    
    Returns:
        LoginResponse: Authentication result returned by the authentication service.
    
    Raises:
        fastapi.HTTPException: Propagates HTTP exceptions from the authentication service.
    """
    return await auth_service.login(login_data)

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
