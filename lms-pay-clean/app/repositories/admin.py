from sqlalchemy import delete, insert, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.admin import AdminModel, GetAdminParamsModel
from app.repositories.abstraction.admin import AbstractAdminRepository
from app.repositories.orm.admin import Admin

class AdminRepository(AbstractAdminRepository):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_user(self, id: int):
        stmt = select(Admin).filter(Admin.id == id)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def list_user(self, params: GetAdminParamsModel):
        stmt = select(Admin)
        result = await self.session.execute(stmt)
        for param in params.__dict__:
            if param == 'page' or param == 'size':
                continue
            stmt = stmt.filter(getattr(Admin, param) == getattr(params, param))
        stmt = stmt.offset(params.page * params.size).limit(params.size)
        return result.scalars().all()
    
    async def create_user(self, user):
        stmt = insert(Admin).values(**user.__dict__).returning(Admin)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def update_user(self, id: int, user):
        stmt = update(Admin).where(Admin.id == id).values(**user.__dict__).returning(Admin)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def delete_user(self, id: int):
        stmt = delete(Admin).where(Admin.id == id)
        await self.session.execute(stmt)
        return None
    
    async def find_user(self, usernameOrEmail: str) -> AdminModel | None:
        stmt = select(Admin).where(or_(Admin.username == usernameOrEmail, Admin.email == usernameOrEmail))
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def deactivate_user(self, id: int):
        stmt = update(Admin).where(Admin.id == id).values(is_active=False).returning(Admin)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def activate_user(self, id: int):
        stmt = update(Admin).where(Admin.id == id).values(is_active=True).returning(Admin)
        result = await self.session.execute(stmt)
        return result.scalar()
    
