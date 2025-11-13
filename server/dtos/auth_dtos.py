from pydantic import BaseModel, EmailStr

# ============================================================================
# INPUT DTOs (Requests)
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None


# ============================================================================
# OUTPUT DTOs (Responses)
# ============================================================================

class LoginResponse(BaseModel):
    message: str
    user_id: str
    email: str
    token: str

class SignupResponse(BaseModel):
    message: str
    user_id: str
    email: str
