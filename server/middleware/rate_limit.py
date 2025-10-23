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
        self.max_attempts = max_attempts
        self.window = timedelta(minutes=window_minutes)
        self.failed_attempts: Dict[str, list] = {}  # Track failed attempts only
        self._cleanup_task = None
    
    async def check_rate_limit(self, identifier: str) -> None:
        """
        Check if the identifier (IP or email) has exceeded rate limit.
        Raises HTTPException if limit exceeded.
        Only checks - doesn't record attempts.
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
        Record a failed login attempt for rate limiting.
        Call this AFTER a login fails.
        """
        now = datetime.now()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(now)
    
    async def reset_attempts(self, identifier: str) -> None:
        """
        Reset/clear failed attempts for an identifier.
        Call this AFTER a successful login.
        """
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    async def cleanup_old_attempts(self):
        """Periodically clean up old attempts to prevent memory leak"""
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
    """Extract client IP from request, considering proxy headers"""
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

