"""
Unit tests for custom error classes.
"""
import pytest
from useCaseHelpers.errors import (
    UseCaseError,
    InputValidationError,
    AuthError,
    QueryError,
    DatabaseError,
    DependencyUnavailableError,
    ConflictError
)


class TestUseCaseError:
    """Tests for base UseCaseError class."""
    
    @pytest.mark.unit
    def test_use_case_error_creation(self):
        """Test creating a basic UseCaseError."""
        error = UseCaseError("Test error message")
        assert str(error) == "USE_CASE_ERROR: Test error message"
        assert error.message == "Test error message"
        assert error.code == "USE_CASE_ERROR"
    
    @pytest.mark.unit
    def test_use_case_error_custom_code(self):
        """Test creating UseCaseError with custom code."""
        error = UseCaseError("Custom error", code="CUSTOM_CODE")
        assert error.code == "CUSTOM_CODE"
        assert str(error) == "CUSTOM_CODE: Custom error"
    
    @pytest.mark.unit
    def test_use_case_error_is_exception(self):
        """Test that UseCaseError is an Exception."""
        error = UseCaseError("Test")
        assert isinstance(error, Exception)


class TestInputValidationError:
    """Tests for InputValidationError."""
    
    @pytest.mark.unit
    def test_input_validation_error_creation(self):
        """Test creating InputValidationError."""
        error = InputValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.code == "INPUT_VALIDATION_ERROR"
        assert str(error) == "INPUT_VALIDATION_ERROR: Invalid input"
    
    @pytest.mark.unit
    def test_input_validation_error_inheritance(self):
        """Test that InputValidationError inherits from UseCaseError."""
        error = InputValidationError("Test")
        assert isinstance(error, UseCaseError)
        assert isinstance(error, Exception)


class TestAuthError:
    """Tests for AuthError."""
    
    @pytest.mark.unit
    def test_auth_error_creation(self):
        """Test creating AuthError."""
        error = AuthError("Authentication failed")
        assert error.message == "Authentication failed"
        assert error.code == "AUTH_ERROR"
    
    @pytest.mark.unit
    def test_auth_error_inheritance(self):
        """Test that AuthError inherits from UseCaseError."""
        error = AuthError("Test")
        assert isinstance(error, UseCaseError)


class TestQueryError:
    """Tests for QueryError."""
    
    @pytest.mark.unit
    def test_query_error_creation(self):
        """Test creating QueryError."""
        error = QueryError("Query failed")
        assert error.message == "Query failed"
        assert error.code == "QUERY_ERROR"
    
    @pytest.mark.unit
    def test_query_error_inheritance(self):
        """Test that QueryError inherits from UseCaseError."""
        error = QueryError("Test")
        assert isinstance(error, UseCaseError)


class TestDatabaseError:
    """Tests for DatabaseError."""
    
    @pytest.mark.unit
    def test_database_error_creation(self):
        """Test creating DatabaseError."""
        error = DatabaseError("Database connection failed")
        assert error.message == "Database connection failed"
        assert error.code == "DATABASE_ERROR"
    
    @pytest.mark.unit
    def test_database_error_inheritance(self):
        """Test that DatabaseError inherits from UseCaseError."""
        error = DatabaseError("Test")
        assert isinstance(error, UseCaseError)


class TestDependencyUnavailableError:
    """Tests for DependencyUnavailableError."""
    
    @pytest.mark.unit
    def test_dependency_unavailable_error_default_message(self):
        """Test creating DependencyUnavailableError with default message."""
        error = DependencyUnavailableError()
        assert error.message == "Required dependency unavailable"
        assert error.code == "DEPENDENCY_UNAVAILABLE"
    
    @pytest.mark.unit
    def test_dependency_unavailable_error_custom_message(self):
        """Test creating DependencyUnavailableError with custom message."""
        error = DependencyUnavailableError("Custom dependency error")
        assert error.message == "Custom dependency error"
    
    @pytest.mark.unit
    def test_dependency_unavailable_error_inheritance(self):
        """Test that DependencyUnavailableError inherits from UseCaseError."""
        error = DependencyUnavailableError()
        assert isinstance(error, UseCaseError)


class TestConflictError:
    """Tests for ConflictError."""
    
    @pytest.mark.unit
    def test_conflict_error_creation(self):
        """Test creating ConflictError."""
        error = ConflictError("Resource conflict")
        assert error.message == "Resource conflict"
        assert error.code == "CONFLICT_ERROR"
    
    @pytest.mark.unit
    def test_conflict_error_inheritance(self):
        """Test that ConflictError inherits from UseCaseError."""
        error = ConflictError("Test")
        assert isinstance(error, UseCaseError)
