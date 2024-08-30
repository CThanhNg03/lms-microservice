from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    usernameOrEmail: str
    password: str

class AdminInfo(BaseModel):
    username: str
    email: str
    is_superuser: Optional[bool] = False

class CreateAdminRequest(AdminInfo):
    password: str

class AdminResponse(AdminInfo):
    id: int
    is_active: bool
    

class LoginResponse(AdminResponse):
    access_token: str
    token_type: str = "bearer"
    