"""Application-layer (use case) custom exceptions.

These are raised by services/use case helpers and translated to HTTP responses
in the interface adapter layer (routes/middleware). Keeping FastAPI's
HTTPException out of domain and use case code aligns with Clean Architecture.
"""

class UseCaseError(Exception):
    """Base application/use-case exception."""
    def __init__(self, message: str, code: str = "USE_CASE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:  # Helpful for logging
        return f"{self.code}: {self.message}"


class InputValidationError(UseCaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code="INPUT_VALIDATION_ERROR")


class AuthError(UseCaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code="AUTH_ERROR")


class QueryError(UseCaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code="QUERY_ERROR")


class DatabaseError(UseCaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code="DATABASE_ERROR")


class DependencyUnavailableError(UseCaseError):
    def __init__(self, message: str = "Required dependency unavailable"):
        super().__init__(message=message, code="DEPENDENCY_UNAVAILABLE")


class ConflictError(UseCaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT_ERROR")
