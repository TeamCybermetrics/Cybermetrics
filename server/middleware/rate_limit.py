from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
from datetime import datetime, timedelta
from config.settings import settings
import asyncio
import json

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
        self.locks: Dict[str, asyncio.Lock] = {}  # Per-identifier locks for thread safety
        self._cleanup_task: asyncio.Task = None
    
    def _get_lock(self, identifier: str) -> asyncio.Lock:
        """
        Get or create a lock for the given identifier.
        
        Parameters:
            identifier (str): Client identifier.
            
        Returns:
            asyncio.Lock: Lock for the identifier.
        """
        if identifier not in self.locks:
            self.locks[identifier] = asyncio.Lock()
        return self.locks[identifier]
    
    async def check_rate_limit(self, identifier: str) -> None:
        """
        Enforce the configured failed-attempts limit for a given identifier.
        
        Thread-safe: Uses per-identifier locks to prevent race conditions.
        Cleans up timestamps older than the rate limit window, counts remaining failed attempts for the identifier, and raises an HTTP 429 error when the configured maximum is reached or exceeded.
        
        Parameters:
            identifier (str): Client identifier to check (e.g., IP address or email).
        
        Raises:
            HTTPException: HTTP 429 Too Many Requests when the identifier has reached or exceeded the allowed failed attempts within the time window.
        """
        now = datetime.now()
        lock = self._get_lock(identifier)
        
        async with lock:
            # Clean up old attempts
            if identifier in self.failed_attempts:
                self.failed_attempts[identifier] = [
                    timestamp for timestamp in self.failed_attempts[identifier]
                    if now - timestamp < self.window
                ]
            
            # Check current failed attempts
            current_attempts = len(self.failed_attempts.get(identifier, []))
            
            if current_attempts >= self.max_attempts:
                minutes = int(self.window.total_seconds() // 60)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Please try again in {minutes} minutes."
                )
    
    async def record_failed_attempt(self, identifier: str) -> None:
        """
        Record a failed authentication attempt for the given identifier.
        
        Thread-safe: Uses per-identifier locks to prevent race conditions.
        
        Parameters:
            identifier (str): Key used to track attempts (for example, a client IP address or username).
        """
        now = datetime.now()
        lock = self._get_lock(identifier)
        
        async with lock:
            if identifier not in self.failed_attempts:
                self.failed_attempts[identifier] = []
            
            self.failed_attempts[identifier].append(now)
    
    async def reset_attempts(self, identifier: str) -> None:
        """
        Clear recorded failed login attempts for the given identifier.
        
        Thread-safe: Uses per-identifier locks to prevent race conditions.
        
        Parameters:
            identifier (str): Identifier whose attempts should be cleared (e.g., client IP or user ID).
        """
        lock = self._get_lock(identifier)
        
        async with lock:
            if identifier in self.failed_attempts:
                del self.failed_attempts[identifier]
            # Clean up the lock as well
            if identifier in self.locks:
                del self.locks[identifier]
    
    async def cleanup_old_attempts(self):
        """
        Continuously prune stored failed-attempt timestamps older than the configured window.
        
        Thread-safe: Uses per-identifier locks to prevent race conditions.
        Removes timestamps for each identifier that are older than the rate limiter's time window and deletes identifiers that have no remaining timestamps. Intended to run indefinitely as a periodic background task (runs every 5 minutes).
        """
        try:
            while True:
                await asyncio.sleep(300)  # Run every 5 minutes
                now = datetime.now()
                
                # Get snapshot of identifiers to avoid dict size change during iteration
                identifiers = list(self.failed_attempts.keys())
                
                for identifier in identifiers:
                    lock = self._get_lock(identifier)
                    
                    async with lock:
                        if identifier in self.failed_attempts:
                            self.failed_attempts[identifier] = [
                                timestamp for timestamp in self.failed_attempts[identifier]
                                if now - timestamp < self.window
                            ]
                            
                            # Remove empty entries and their locks
                            if not self.failed_attempts[identifier]:
                                del self.failed_attempts[identifier]
                                if identifier in self.locks:
                                    del self.locks[identifier]
        except asyncio.CancelledError:
            # Cleanup task was cancelled, exit gracefully
            pass
    
    def start_cleanup_task(self) -> None:
        """
        Start the background cleanup task.
        Should be called once during application startup.
        """
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self.cleanup_old_attempts())
    
    async def stop_cleanup_task(self) -> None:
        """
        Stop the background cleanup task.
        Should be called during application shutdown.
        """
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

# Singleton instance
rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)


async def get_client_ip(request: Request) -> str:
    """
    Return the client's IP address using common proxy headers or the request's peer address.
    
    SECURITY: Only trusts X-Forwarded-For/X-Real-IP headers when TRUST_PROXY is enabled.
    When TRUST_PROXY=false (default), ignores proxy headers to prevent IP spoofing.
    When TRUST_PROXY=true, prefers the first IP in X-Forwarded-For, then X-Real-IP.
    Always falls back to request.client.host if headers are unavailable or untrusted.
    
    IMPORTANT: Only enable TRUST_PROXY when running behind a trusted reverse proxy
    (e.g., nginx, Cloudflare) that strips client-supplied forward headers.
    
    Parameters:
        request (Request): FastAPI request object to inspect for client IP information.
    
    Returns:
        ip (str): The determined client IP address, or "unknown" if unavailable.
    """
    # Only trust proxy headers if explicitly configured
    if settings.TRUST_PROXY:
        # Check for X-Forwarded-For header (proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP (closest to client)
            ip = forwarded.split(",")[0].strip()
            # Basic validation - ensure it's not empty
            if ip:
                return ip
        
        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip and real_ip.strip():
            return real_ip.strip()
    
    # Fallback to direct client IP (always safe)
    return request.client.host if request.client else "unknown"


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
