from app.di.unit_of_work import AbstractUnitOfWork
from app.model.admin import CreateAdminModel, GetAdminParamsModel
from app.repositories.abstraction.admin import AbstractAdminRepository
from app.setting.security import get_password_hash

async def get_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user_id: int):
    async with async_unit_of_work as uow:
        return await uow.repo.get_user(user_id)

async def list_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], params: GetAdminParamsModel):
    async with async_unit_of_work as uow:
        return await uow.repo.list_user(params)

async def create_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user: CreateAdminModel):
    async with async_unit_of_work as uow:
        user.password = get_password_hash(user.password)
        return await uow.repo.create_user(user)

async def update_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user_id: int, user: CreateAdminModel):
    async with async_unit_of_work as uow:
        return await uow.repo.update_user(user_id, user)

async def delete_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user_id: int):
    async with async_unit_of_work as uow:
        return await uow.repo.delete_user(user_id)
    
async def find_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], usernameOrEmail: str):
    async with async_unit_of_work as uow:
        return await uow.repo.find_user(usernameOrEmail)

async def deactivate_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user_id: int):
    async with async_unit_of_work as uow:
        return await uow.repo.deactivate_user(user_id)

async def activate_user(async_unit_of_work: AbstractUnitOfWork[AbstractAdminRepository], user_id: int):
    async with async_unit_of_work as uow:
        return await uow.repo.activate_user(user_id)
        

    