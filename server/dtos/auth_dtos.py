from pydantic import BaseModel, EmailStr

# ============================================================================
# INPUT DTOs (Requests)
# ============================================================================

class LoginRequest(BaseModel):
    """Request payload for user login"""
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    """Request payload for user registration"""
    email: EmailStr
    password: str
    display_name: str | None = None


# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class LoginResponse(BaseModel):
    """Response returned after successful login"""
    message: str
    user_id: str
    email: str
    token: str
    display_name: str | None = None

class SignupResponse(BaseModel):
    """Response returned after successful user registration"""
    message: str
    user_id: str
    email: str
