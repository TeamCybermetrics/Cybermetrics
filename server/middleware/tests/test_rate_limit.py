"""
Unit tests for RateLimiter class.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi import HTTPException
from middleware.rate_limit import RateLimiter


class TestRateLimiterInitialization:
    """Tests for RateLimiter initialization."""
    
    @pytest.mark.unit
    def test_rate_limiter_default_initialization(self):
        """Test RateLimiter with default parameters."""
        limiter = RateLimiter()
        assert limiter.max_attempts == 5
        assert limiter.window == timedelta(minutes=15)
        assert limiter.failed_attempts == {}
        assert limiter.locks == {}
    
    @pytest.mark.unit
    def test_rate_limiter_custom_initialization(self):
        """Test RateLimiter with custom parameters."""
        limiter = RateLimiter(max_attempts=3, window_minutes=10)
        assert limiter.max_attempts == 3
        assert limiter.window == timedelta(minutes=10)
    
    @pytest.mark.unit
    def test_rate_limiter_custom_max_attempts(self):
        """Test RateLimiter with custom max attempts."""
        limiter = RateLimiter(max_attempts=10)
        assert limiter.max_attempts == 10
        assert limiter.window == timedelta(minutes=15)  # Default
    
    @pytest.mark.unit
    def test_rate_limiter_custom_window(self):
        """Test RateLimiter with custom window."""
        limiter = RateLimiter(window_minutes=30)
        assert limiter.max_attempts == 5  # Default
        assert limiter.window == timedelta(minutes=30)


class TestRateLimiterLocks:
    """Tests for RateLimiter lock management."""
    
    @pytest.mark.unit
    def test_get_lock_creates_new_lock(self):
        """Test that _get_lock creates a new lock for new identifier."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        lock = limiter._get_lock(identifier)
        assert isinstance(lock, asyncio.Lock)
        assert identifier in limiter.locks
    
    @pytest.mark.unit
    def test_get_lock_returns_same_lock(self):
        """Test that _get_lock returns the same lock for same identifier."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        lock1 = limiter._get_lock(identifier)
        lock2 = limiter._get_lock(identifier)
        
        assert lock1 is lock2
    
    @pytest.mark.unit
    def test_get_lock_different_identifiers(self):
        """Test that different identifiers get different locks."""
        limiter = RateLimiter()
        
        lock1 = limiter._get_lock("user1")
        lock2 = limiter._get_lock("user2")
        
        assert lock1 is not lock2
        assert len(limiter.locks) == 2


class TestRateLimiterCheckRateLimit:
    """Tests for check_rate_limit method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_rate_limit_first_attempt(self):
        """Test that first attempt passes without error."""
        limiter = RateLimiter(max_attempts=5)
        identifier = "test_user"
        
        # Should not raise exception
        await limiter.check_rate_limit(identifier)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_rate_limit_within_limit(self):
        """Test that attempts within limit pass."""
        limiter = RateLimiter(max_attempts=5)
        identifier = "test_user"
        
        # Record 4 failed attempts
        for _ in range(4):
            await limiter.record_failed_attempt(identifier)
        
        # 5th check should still pass (we haven't hit the limit yet)
        await limiter.check_rate_limit(identifier)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeds_limit(self):
        """Test that exceeding limit raises HTTPException."""
        limiter = RateLimiter(max_attempts=3)
        identifier = "test_user"
        
        # Record 3 failed attempts
        for _ in range(3):
            await limiter.record_failed_attempt(identifier)
        
        # Next check should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await limiter.check_rate_limit(identifier)
        
        assert exc_info.value.status_code == 429
        assert "Too many failed" in str(exc_info.value.detail)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_rate_limit_different_identifiers(self):
        """Test that different identifiers are tracked separately."""
        limiter = RateLimiter(max_attempts=2)
        
        # Record 2 failed attempts for user1
        await limiter.record_failed_attempt("user1")
        await limiter.record_failed_attempt("user1")
        
        # user2 should still be able to make requests
        await limiter.check_rate_limit("user2")
        
        # user1 should be blocked
        with pytest.raises(HTTPException):
            await limiter.check_rate_limit("user1")


class TestRateLimiterRecordFailedAttempt:
    """Tests for record_failed_attempt method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_record_failed_attempt_creates_entry(self):
        """Test that recording failed attempt creates entry."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        await limiter.record_failed_attempt(identifier)
        
        assert identifier in limiter.failed_attempts
        assert len(limiter.failed_attempts[identifier]) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_record_failed_attempt_multiple_times(self):
        """Test recording multiple failed attempts."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        await limiter.record_failed_attempt(identifier)
        await limiter.record_failed_attempt(identifier)
        await limiter.record_failed_attempt(identifier)
        
        assert len(limiter.failed_attempts[identifier]) == 3
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_record_failed_attempt_timestamps(self):
        """Test that failed attempts have timestamps."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        before = datetime.now()
        await limiter.record_failed_attempt(identifier)
        after = datetime.now()
        
        timestamp = limiter.failed_attempts[identifier][0]
        assert isinstance(timestamp, datetime)
        assert before <= timestamp <= after


class TestRateLimiterResetAttempts:
    """Tests for reset_attempts method."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reset_attempts_removes_entry(self):
        """Test that reset_attempts removes identifier entry."""
        limiter = RateLimiter()
        identifier = "test_user"
        
        # Record some attempts
        await limiter.record_failed_attempt(identifier)
        await limiter.record_failed_attempt(identifier)
        
        # Reset attempts
        await limiter.reset_attempts(identifier)
        
        assert identifier not in limiter.failed_attempts
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reset_attempts_nonexistent_identifier(self):
        """Test that resetting nonexistent identifier doesn't raise error."""
        limiter = RateLimiter()
        
        # Should not raise exception
        await limiter.reset_attempts("nonexistent_user")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reset_attempts_allows_new_requests(self):
        """Test that resetting attempts allows new requests."""
        limiter = RateLimiter(max_attempts=2)
        identifier = "test_user"
        
        # Hit the limit
        await limiter.record_failed_attempt(identifier)
        await limiter.record_failed_attempt(identifier)
        
        # Should be blocked
        with pytest.raises(HTTPException):
            await limiter.check_rate_limit(identifier)
        
        # Reset attempts
        await limiter.reset_attempts(identifier)
        
        # Should now be allowed
        await limiter.check_rate_limit(identifier)


class TestRateLimiterEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_zero_max_attempts(self):
        """Test rate limiter with zero max attempts."""
        limiter = RateLimiter(max_attempts=0)
        
        # Should immediately block
        with pytest.raises(HTTPException):
            await limiter.check_rate_limit("test_user")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_one_max_attempt(self):
        """Test rate limiter with one max attempt."""
        limiter = RateLimiter(max_attempts=1)
        identifier = "test_user"
        
        # First check should pass
        await limiter.check_rate_limit(identifier)
        
        # Record one failed attempt
        await limiter.record_failed_attempt(identifier)
        
        # Should now be blocked
        with pytest.raises(HTTPException):
            await limiter.check_rate_limit(identifier)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_empty_identifier(self):
        """Test rate limiter with empty string identifier."""
        limiter = RateLimiter()
        
        # Should handle empty string
        await limiter.check_rate_limit("")
        await limiter.record_failed_attempt("")
        
        assert "" in limiter.failed_attempts
