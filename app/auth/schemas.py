from pydantic import BaseModel, EmailStr, constr
from typing import Annotated
from enum import Enum

StrongPasswordStr = Annotated[
    str,
    constr(
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])"
    )
]

class Role(str, Enum):
    admin = "admin"
    user = "user"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: StrongPasswordStr
    role: Role = Role.user

class UserLogin(BaseModel):
    email: EmailStr
    password: StrongPasswordStr

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: StrongPasswordStr