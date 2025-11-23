"""
Unit tests for error handler middleware.
"""
import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from middleware.error_handler import validation_exception_handler, general_exception_handler


class TestValidationExceptionHandler:
    """Tests for validation_exception_handler."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """Test that validation errors are handled correctly."""
        from unittest.mock import Mock
        
        # Create mock request
        request = Mock(spec=Request)
        
        # Create a validation error
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                name: str
                age: int
            
            TestModel(name="test", age="not_an_int")
        except ValidationError as e:
            exc = RequestValidationError(errors=e.errors())
        
        # Call handler
        response = await validation_exception_handler(request, exc)
        
        # Verify response
        assert response.status_code == 422
        assert "detail" in response.body.decode()
        assert "Validation error" in response.body.decode()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validation_exception_includes_errors(self):
        """Test that validation exception response includes error details."""
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                email: str
            
            TestModel(email=123)
        except ValidationError as e:
            exc = RequestValidationError(errors=e.errors())
        
        response = await validation_exception_handler(request, exc)
        
        # Response should include errors
        assert response.status_code == 422
        body = response.body.decode()
        assert "errors" in body


class TestGeneralExceptionHandler:
    """Tests for general_exception_handler."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test that general exceptions are handled correctly."""
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        exc = Exception("Test error")
        
        response = await general_exception_handler(request, exc)
        
        assert response.status_code == 500
        body = response.body.decode()
        assert "Internal server error" in body
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_general_exception_different_errors(self):
        """Test handling of different exception types."""
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        
        # Test with ValueError
        exc = ValueError("Invalid value")
        response = await general_exception_handler(request, exc)
        assert response.status_code == 500
        
        # Test with RuntimeError
        exc = RuntimeError("Runtime issue")
        response = await general_exception_handler(request, exc)
        assert response.status_code == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_general_exception_hides_details(self):
        """Test that exception details are not exposed to client."""
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        exc = Exception("Sensitive database connection string: password123")
        
        response = await general_exception_handler(request, exc)
        
        body = response.body.decode()
        # Should not expose the actual error message
        assert "password123" not in body
        assert "Internal server error" in body
