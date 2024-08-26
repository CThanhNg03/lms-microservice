from injector import Injector, Module, provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.unit_of_work import AbstractUnitOfWork, SQLUnitOfWork
from app.repositories.payment import PaymentRepository

class DBModule(Module):
    @provider
    async def provide_session(self) -> AsyncSession:
        from app.setting.db import get_session

        return await get_session()
    
    @provider
    def provide_repo(self, session: AsyncSession) -> PaymentRepository:
        return PaymentRepository(session)
    
    @provider
    def provide_db_uow(self, session: AsyncSession, repo: PaymentRepository) -> AbstractUnitOfWork:
        return SQLUnitOfWork(repo, session)
    
injector = Injector([DBModule()])