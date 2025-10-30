import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from middleware.rate_limit import RateLimiter, get_client_ip


class TestRateLimiter:
    """Unit tests for RateLimiter"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.rate_limiter = RateLimiter(max_attempts=3, window_minutes=15)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_first_attempt(self):
        """Test rate limit check passes on first attempt"""
        identifier = "192.168.1.1"
        
        # Should not raise exception
        await self.rate_limiter.check_rate_limit(identifier)
    
    @pytest.mark.asyncio
    async def test_record_failed_attempt(self):
        """Test recording failed attempts"""
        identifier = "192.168.1.1"
        
        await self.rate_limiter.record_failed_attempt(identifier)
        
        # Verify attempt was recorded
        assert identifier in self.rate_limiter.failed_attempts
        assert len(self.rate_limiter.failed_attempts[identifier]) == 1
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_under_threshold(self):
        """Test rate limit check passes when under threshold"""
        identifier = "192.168.1.1"
        
        # Record 2 failed attempts (under max of 3)
        await self.rate_limiter.record_failed_attempt(identifier)
        await self.rate_limiter.record_failed_attempt(identifier)
        
        # Should not raise exception
        await self.rate_limiter.check_rate_limit(identifier)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_at_threshold(self):
        """Test rate limit check fails when at threshold"""
        identifier = "192.168.1.1"
        
        # Record 3 failed attempts (at max)
        for _ in range(3):
            await self.rate_limiter.record_failed_attempt(identifier)
        
        # Should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await self.rate_limiter.check_rate_limit(identifier)
        
        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Too many failed login attempts" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_over_threshold(self):
        """Test rate limit check fails when over threshold"""
        identifier = "192.168.1.1"
        
        # Record 5 failed attempts (over max of 3)
        for _ in range(5):
            await self.rate_limiter.record_failed_attempt(identifier)
        
        # Should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await self.rate_limiter.check_rate_limit(identifier)
        
        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    @pytest.mark.asyncio
    async def test_reset_attempts(self):
        """Test resetting failed attempts"""
        identifier = "192.168.1.1"
        
        # Record failed attempts
        for _ in range(3):
            await self.rate_limiter.record_failed_attempt(identifier)
        
        # Reset attempts
        await self.rate_limiter.reset_attempts(identifier)
        
        # Verify attempts were cleared
        assert identifier not in self.rate_limiter.failed_attempts
        
        # Should pass rate limit check now
        await self.rate_limiter.check_rate_limit(identifier)
    
    @pytest.mark.asyncio
    async def test_reset_attempts_nonexistent_identifier(self):
        """Test resetting attempts for identifier that doesn't exist"""
        identifier = "192.168.1.1"
        
        # Should not raise exception
        await self.rate_limiter.reset_attempts(identifier)
    
    @pytest.mark.asyncio
    async def test_multiple_identifiers(self):
        """Test rate limiter tracks multiple identifiers separately"""
        identifier1 = "192.168.1.1"
        identifier2 = "192.168.1.2"
        
        # Record attempts for identifier1
        for _ in range(3):
            await self.rate_limiter.record_failed_attempt(identifier1)
        
        # identifier1 should be rate limited
        with pytest.raises(HTTPException):
            await self.rate_limiter.check_rate_limit(identifier1)
        
        # identifier2 should not be rate limited
        await self.rate_limiter.check_rate_limit(identifier2)
    
    @pytest.mark.asyncio
    async def test_cleanup_old_attempts(self):
        """Test cleanup removes old attempts outside window"""
        identifier = "192.168.1.1"
        
        # Manually add old timestamp (outside window)
        old_timestamp = datetime.now() - timedelta(minutes=20)
        self.rate_limiter.failed_attempts[identifier] = [old_timestamp]
        
        # Check rate limit (should clean up old attempts)
        await self.rate_limiter.check_rate_limit(identifier)
        
        # Old attempts should be cleaned up
        assert len(self.rate_limiter.failed_attempts.get(identifier, [])) == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_keeps_recent_attempts(self):
        """Test cleanup keeps recent attempts within window"""
        identifier = "192.168.1.1"
        
        # Add recent timestamp
        recent_timestamp = datetime.now() - timedelta(minutes=5)
        self.rate_limiter.failed_attempts[identifier] = [recent_timestamp]
        
        # Check rate limit
        await self.rate_limiter.check_rate_limit(identifier)
        
        # Recent attempts should be kept
        assert len(self.rate_limiter.failed_attempts[identifier]) == 1
    
    @pytest.mark.asyncio
    async def test_mixed_old_and_recent_attempts(self):
        """Test cleanup handles mix of old and recent attempts"""
        identifier = "192.168.1.1"
        
        # Add mix of old and recent timestamps
        old_timestamp = datetime.now() - timedelta(minutes=20)
        recent_timestamp1 = datetime.now() - timedelta(minutes=5)
        recent_timestamp2 = datetime.now() - timedelta(minutes=2)
        
        self.rate_limiter.failed_attempts[identifier] = [
            old_timestamp,
            recent_timestamp1,
            recent_timestamp2
        ]
        
        # Check rate limit
        await self.rate_limiter.check_rate_limit(identifier)
        
        # Only recent attempts should remain
        assert len(self.rate_limiter.failed_attempts[identifier]) == 2
    
    @pytest.mark.asyncio
    async def test_custom_max_attempts(self):
        """Test rate limiter with custom max attempts"""
        rate_limiter = RateLimiter(max_attempts=5, window_minutes=10)
        identifier = "192.168.1.1"
        
        # Record 4 attempts (under max of 5)
        for _ in range(4):
            await rate_limiter.record_failed_attempt(identifier)
        
        # Should not raise exception
        await rate_limiter.check_rate_limit(identifier)
        
        # Record 5th attempt
        await rate_limiter.record_failed_attempt(identifier)
        
        # Should raise exception now
        with pytest.raises(HTTPException):
            await rate_limiter.check_rate_limit(identifier)


class TestGetClientIP:
    """Unit tests for get_client_ip function"""
    
    @pytest.mark.asyncio
    async def test_get_client_ip_from_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-Forwarded-For": "203.0.113.1, 198.51.100.1"
        }.get(key))
        
        ip = await get_client_ip(mock_request)
        
        # Should return first IP in the list
        assert ip == "203.0.113.1"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_from_x_real_ip(self):
        """Test getting client IP from X-Real-IP header"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-Real-IP": "203.0.113.1"
        }.get(key))
        
        ip = await get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_from_request_client(self):
        """Test getting client IP from request.client"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(return_value=None)
        mock_request.client = Mock()
        mock_request.client.host = "203.0.113.1"
        
        ip = await get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_priority(self):
        """Test X-Forwarded-For has priority over X-Real-IP"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-Forwarded-For": "203.0.113.1",
            "X-Real-IP": "198.51.100.1"
        }.get(key))
        
        ip = await get_client_ip(mock_request)
        
        # Should return X-Forwarded-For value
        assert ip == "203.0.113.1"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_no_client(self):
        """Test getting client IP when request.client is None"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(return_value=None)
        mock_request.client = None
        
        ip = await get_client_ip(mock_request)
        
        assert ip == "unknown"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_strips_whitespace(self):
        """Test getting client IP strips whitespace"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-Forwarded-For": "  203.0.113.1  , 198.51.100.1"
        }.get(key))
        
        ip = await get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
