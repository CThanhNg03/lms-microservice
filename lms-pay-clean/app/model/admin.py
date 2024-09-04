from dataclasses import dataclass


@dataclass
class AdminInfoModel:
    id: int
    username: str

@dataclass
class AdminResponseModel(AdminInfoModel):
    email: str
    is_active: bool
    is_superuser: bool

@dataclass
class AdminModel(AdminResponseModel):
    password: str

@dataclass
class CreateAdminModel:
    username: str
    password: str
    email: str

@dataclass
class UpdateAdminModel:
    username: str
    password: str
    email: str
    is_active: bool
    is_superuser: bool

@dataclass
class LoginParamModel:
    usernameOrEmail: str
    password: str

@dataclass
class GetAdminParamsModel:
    page: int = 1
    size: int = 10
    username: str = None
    email: str = None
    is_active: bool = None
    is_superuser: bool = None
    order_by: str = None
    order_type: str = None

