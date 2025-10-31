"""
Rate limiting middleware for authentication endpoints.
Applies rate limiting globally to auth routes and manages success/failure tracking.
"""
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from middleware.rate_limit import rate_limiter, get_client_ip
import json


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to authentication endpoints.
    
    Handles:
    - Pre-request rate limit checks
    - Post-response success/failure tracking
    - Different strategies for signup vs login
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting for auth endpoints.
        
        Parameters:
            request: The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            Response from the route handler or rate limit error
        """
        # Only apply to auth endpoints
        if not request.url.path.startswith("/api/auth"):
            return await call_next(request)
        
        # Skip rate limiting for token verification
        if request.url.path == "/api/auth/verify":
            return await call_next(request)
        
        # Get client IP
        client_ip = await get_client_ip(request)
        
        # Determine endpoint type
        is_signup = request.url.path == "/api/auth/signup"
        is_login = request.url.path == "/api/auth/login"
        
        if not (is_signup or is_login):
            return await call_next(request)
        
        try:
            # Check IP-based rate limit
            if is_signup:
                await rate_limiter.check_rate_limit(f"signup:{client_ip}")
            elif is_login:
                await rate_limiter.check_rate_limit(f"login:ip:{client_ip}")
                
                # For login, also check email-based rate limit
                # Need to read request body
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        email = data.get("email")
                        if email:
                            await rate_limiter.check_rate_limit(f"login:email:{email}")
                            # Store email in request state for later use
                            request.state.email = email
                    except json.JSONDecodeError:
                        pass
                
                # Recreate request with body (since we consumed it)
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            
            # Process the request
            response = await call_next(request)
            
            # Handle success/failure based on response status
            if is_login:
                email = getattr(request.state, "email", None)
                
                if response.status_code == 200:
                    # Login succeeded - reset counters
                    await rate_limiter.reset_attempts(f"login:ip:{client_ip}")
                    if email:
                        await rate_limiter.reset_attempts(f"login:email:{email}")
                        
                elif response.status_code == 401:
                    # Login failed - record attempts
                    await rate_limiter.record_failed_attempt(f"login:ip:{client_ip}")
                    if email:
                        await rate_limiter.record_failed_attempt(f"login:email:{email}")
            
            return response
            
        except Exception as e:
            # If it's an HTTPException from rate limiter, return proper JSON response
            if hasattr(e, 'status_code') and hasattr(e, 'detail'):
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
            raise
