from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    semester: Optional[str] = None
    department: Optional[str] = None
    # Admin accounts should be created manually / via seed script, never via
    # public self-registration. This field only allows STUDENT at signup.


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    name: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    semester: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True
