from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    active_role: str  # empty string if not set yet


class ActiveRoleRequest(BaseModel):
    role: str  # validated against UserRole in service layer


class ActiveRoleResponse(BaseModel):
    user_id: str
    active_role: str
    message: str
