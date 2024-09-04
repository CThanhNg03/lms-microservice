
from math import e
from typing import Annotated
from fastapi import Depends, HTTPException

from app.model.admin import AdminResponseModel
from app.setting.security import decode_token, oauth2_scheme


OAuth2Dep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(token: OAuth2Dep) -> AdminResponseModel:
    id, username, email, active, super = decode_token(token).get("sub").split(":")
    if not username:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return AdminResponseModel(
        id=int(id),
        username=username,
        email=email,
        is_active=active=="active",
        is_superuser=super=="superuser"
    )

GetUserDep = Annotated[AdminResponseModel, Depends(get_current_user)]

async def get_current_active_user(current_user: GetUserDep) -> AdminResponseModel:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

GetActiveUserDep = Annotated[AdminResponseModel, Depends(get_current_active_user)]

async def get_current_active_superuser(current_user: GetActiveUserDep) -> AdminResponseModel:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not a superuser")
    return current_user

GetSuperUserDep = Annotated[AdminResponseModel, Depends(get_current_active_superuser)]


