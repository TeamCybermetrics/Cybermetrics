from fastapi import HTTPException, Request, status
from typing import Dict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    """
    Simple in-memory rate limiter for login attempts.
    For production, use Redis or a proper rate limiting service.
    """
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        """
        Initialize a RateLimiter that tracks failed attempts per identifier within a rolling time window.
        
        Parameters:
            max_attempts (int): Maximum allowed failed attempts inside the time window before the limiter triggers.
            window_minutes (int): Length of the rolling time window in minutes used to count failed attempts.
        """
        self.max_attempts = max_attempts
        self.window = timedelta(minutes=window_minutes)
        self.failed_attempts: Dict[str, list] = {}  # Track failed attempts only
        self._cleanup_task = None
    
    async def check_rate_limit(self, identifier: str) -> None:
        """
        Enforce the configured failed-attempts limit for a given identifier.
        
        Cleans up timestamps older than the rate limit window, counts remaining failed attempts for the identifier, and raises an HTTP 429 error when the configured maximum is reached or exceeded.
        
        Parameters:
            identifier (str): Client identifier to check (e.g., IP address or email).
        
        Raises:
            HTTPException: HTTP 429 Too Many Requests when the identifier has reached or exceeded the allowed failed attempts within the time window.
        """
        now = datetime.now()
        
        # Clean up old attempts
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                timestamp for timestamp in self.failed_attempts[identifier]
                if now - timestamp < self.window
            ]
        
        # Check current failed attempts
        current_attempts = len(self.failed_attempts.get(identifier, []))
        
        if current_attempts >= self.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Please try again in {self.window.seconds // 60} minutes."
            )
    
    async def record_failed_attempt(self, identifier: str) -> None:
        """
        Record a failed authentication attempt for the given identifier.
        
        Parameters:
            identifier (str): Key used to track attempts (for example, a client IP address or username).
        """
        now = datetime.now()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(now)
    
    async def reset_attempts(self, identifier: str) -> None:
        """
        Clear recorded failed login attempts for the given identifier.
        
        Parameters:
            identifier (str): Identifier whose attempts should be cleared (e.g., client IP or user ID).
        """
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    async def cleanup_old_attempts(self):
        """
        Continuously prune stored failed-attempt timestamps older than the configured window.
        
        Removes timestamps for each identifier that are older than the rate limiter's time window and deletes identifiers that have no remaining timestamps. Intended to run indefinitely as a periodic background task (runs every 5 minutes).
        """
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            now = datetime.now()
            
            for identifier in list(self.failed_attempts.keys()):
                self.failed_attempts[identifier] = [
                    timestamp for timestamp in self.failed_attempts[identifier]
                    if now - timestamp < self.window
                ]
                
                # Remove empty entries
                if not self.failed_attempts[identifier]:
                    del self.failed_attempts[identifier]

# Singleton instance
rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)


async def get_client_ip(request: Request) -> str:
    """
    Return the client's IP address using common proxy headers or the request's peer address.
    
    Prefers the first IP in the `X-Forwarded-For` header, then `X-Real-IP`, and falls back to `request.client.host`; returns the string `"unknown"` if no IP can be determined.
    
    Parameters:
        request (Request): FastAPI request object to inspect for client IP information.
    
    Returns:
        ip (str): The determined client IP address, or `"unknown"` if unavailable.
    """
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


# Rate limiting dependencies
async def rate_limit_signup(request: Request) -> str:
    """
    Dependency to check rate limits for signup endpoint by IP.
    Returns the client IP for use in the route handler.
    """
    client_ip = await get_client_ip(request)
    await rate_limiter.check_rate_limit(f"signup:{client_ip}")
    return client_ip


async def rate_limit_login(request: Request) -> str:
    """
    Dependency to check rate limits for login endpoint by IP.
    Returns the client IP for use in the route handler.
    Note: Email-based rate limiting is handled in the route due to need for request body.
    """
    client_ip = await get_client_ip(request)
    await rate_limiter.check_rate_limit(f"login:ip:{client_ip}")
    return client_ip
