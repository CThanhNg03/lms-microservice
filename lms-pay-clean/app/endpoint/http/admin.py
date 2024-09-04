from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse

from app.common.dependencies.auth import GetActiveUserDep, GetSuperUserDep
from app.di.unit_of_work import AbstractUnitOfWork
from app.endpoint.schema.admin import AdminResponse, CreateAdminRequest, LoginResponse
from app.di.dependency_injection import admin_injector
from app.setting.security import create_access_token, verify_password
from app.usecase import admin as admin_uc
from app.setting.setting import logger

admin = APIRouter(tags=["admin"])


@admin.get("/", response_class=HTMLResponse)
async def admin_index():
    return "<h1>Go to <a href='/docs'>/docs</a></h1>"

@admin.post("/login", response_model=LoginResponse)
async def admin_login(body: Annotated[OAuth2PasswordRequestForm, Depends()]):
    auow = admin_injector.get(AbstractUnitOfWork)
    user = await admin_uc.find_user(auow, body.username)
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    active = "active" if user.is_active else "inactive"
    super = "superuser" if user.is_superuser else "notsuperuser"
    return LoginResponse(
        access_token = create_access_token({"sub": f"{user.id}:{user.username}:{user.email}:{active}:{super}"}),
        **user.__dict__
    )

@admin.get("/me", response_model=AdminResponse)
async def admin_me(user: GetActiveUserDep):
    auow = admin_injector.get(AbstractUnitOfWork)
    user = await admin_uc.get_user(auow, user.id)
    return AdminResponse(**user.__dict__)

@admin.get("/logout")
async def admin_logout():
    pass

@admin.post("/user", response_model=AdminResponse, status_code=201)
async def create_user(body: CreateAdminRequest, admin: GetSuperUserDep):
    auow = admin_injector.get(AbstractUnitOfWork)
    return await admin_uc.create_user(auow, body)
