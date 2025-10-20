from fastapi import Header, HTTPException, status, Depends
from dependency.dependencies import get_auth_service
from services.auth_service import AuthService

async def get_current_user(
    authorization: str = Header(None), 
    auth_service: AuthService = Depends(get_auth_service)
    ) -> str:
    """
    Dependency to extract and verify the current user from the Authorization header.
    Returns the user_id (uid) of the authenticated user.
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
    
    # Verify token and get user info
    user_info = await auth_service.verify_token(token)
    
    # Return just the user_id for use in routes
    return user_info["user_id"]

