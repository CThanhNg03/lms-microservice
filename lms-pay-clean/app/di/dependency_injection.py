from typing import Type, TypeVar
from injector import Injector, Module, provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.unit_of_work import AbstractUnitOfWork, SQLUnitOfWork
from app.model import admin
from app.repositories.abstraction.payment import AbstractPaymentRepository
from app.repositories.admin import AdminRepository
from app.repositories.payment import PaymentRepository

T = TypeVar("T", bound=AbstractPaymentRepository)

class DBModule(Module):
    def __init__(self, repo_cls: Type[T]):
        self.repo_cls = repo_cls
        
    @provider
    def provide_session(self) -> AsyncSession:
        from app.setting.db import get_session

        return get_session()
    
    @provider
    def provide_repo(self, session: AsyncSession) -> T:
        return self.repo_cls(session)
    
    @provider
    def provide_db_uow(self, session: AsyncSession, repo: T) -> AbstractUnitOfWork:
        return SQLUnitOfWork(repo, session)
    
payment_injector = Injector([DBModule(PaymentRepository)])
admin_injector = Injector([DBModule(AdminRepository)])