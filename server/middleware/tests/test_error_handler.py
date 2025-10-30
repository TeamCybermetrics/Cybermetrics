import pytest
from unittest.mock import Mock
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from middleware.error_handler import validation_exception_handler, general_exception_handler


class TestErrorHandler:
    """Unit tests for error handler middleware"""
    
    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """Test validation exception handler returns proper response"""
        # Create mock request
        mock_request = Mock(spec=Request)
        
        # Create a validation error
        try:
            from pydantic import BaseModel, Field
            
            class TestModel(BaseModel):
                name: str = Field(..., min_length=1)
                age: int = Field(..., gt=0)
            
            TestModel(name="", age=-1)
        except ValidationError as e:
            validation_error = RequestValidationError(errors=e.errors())
        
        # Call handler
        response = await validation_exception_handler(mock_request, validation_error)
        
        # Verify response
        assert response.status_code == 422
        assert "detail" in response.body.decode()
        assert "Validation error" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_validation_exception_handler_includes_errors(self):
        """Test validation exception handler includes error details"""
        mock_request = Mock(spec=Request)
        
        # Create a validation error with specific field errors
        try:
            from pydantic import BaseModel
            
            class TestModel(BaseModel):
                email: str
                age: int
            
            TestModel(email=123, age="not_a_number")
        except ValidationError as e:
            validation_error = RequestValidationError(errors=e.errors())
        
        response = await validation_exception_handler(mock_request, validation_error)
        
        # Verify response includes errors
        assert response.status_code == 422
        body = response.body.decode()
        assert "errors" in body
    
    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test general exception handler returns 500 error"""
        mock_request = Mock(spec=Request)
        exception = Exception("Something went wrong")
        
        response = await general_exception_handler(mock_request, exception)
        
        # Verify response
        assert response.status_code == 500
        body = response.body.decode()
        assert "Internal server error" in body
    
    @pytest.mark.asyncio
    async def test_general_exception_handler_hides_details(self):
        """Test general exception handler doesn't expose internal error details"""
        mock_request = Mock(spec=Request)
        exception = Exception("Sensitive database connection error")
        
        response = await general_exception_handler(mock_request, exception)
        
        # Verify response doesn't include sensitive details
        body = response.body.decode()
        assert "database" not in body.lower()
        assert "Internal server error" in body
    
    @pytest.mark.asyncio
    async def test_general_exception_handler_various_exceptions(self):
        """Test general exception handler handles different exception types"""
        mock_request = Mock(spec=Request)
        
        # Test with different exception types
        exceptions = [
            ValueError("Invalid value"),
            KeyError("Missing key"),
            AttributeError("Missing attribute"),
            RuntimeError("Runtime error")
        ]
        
        for exc in exceptions:
            response = await general_exception_handler(mock_request, exc)
            assert response.status_code == 500
            assert "Internal server error" in response.body.decode()
