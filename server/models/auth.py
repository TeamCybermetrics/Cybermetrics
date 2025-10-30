from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: str
    email: str
    token: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

class SignupResponse(BaseModel):
    message: str
    user_id: str
    email: str

class User(BaseModel):  # ← Add this
    user_id: str
    email: str
    name: str

