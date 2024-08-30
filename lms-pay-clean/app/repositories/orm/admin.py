from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped
from app.endpoint.schema.admin import AdminInfo
from app.model.admin import AdminInfoModel, AdminModel
from app.repositories.orm.base import Base


class Admin(Base):
    __tablename__ = 'admin'

    id: Mapped[int]= Column(Integer, primary_key=True)
    username: Mapped[str] = Column(String, unique=True)
    password: Mapped[str] = Column(String)
    email: Mapped[str] = Column(String, unique=True)
    full_name: Mapped[str] = Column(String)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    is_superuser: Mapped[bool] = Column(Boolean, default=False)

    def __init__(self, *, username, password, email, full_name):
        self.username = username
        self.password = password
        self.email = email
        self.full_name = full_name
        self.is_active = True
        self.is_superuser = False
    
    def asDataClass(self) -> AdminModel:
        if self is None:
            return None
        return AdminModel(
            id=self.id,
            username=self.username,
            password=self.password,
            email=self.email,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=self.is_superuser
        )