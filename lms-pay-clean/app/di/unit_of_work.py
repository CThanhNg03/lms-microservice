import abc
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.abstraction.payment import AbstractPaymentRepository
from app.repositories.payment import PaymentRepository

T = TypeVar("T", bound=AbstractPaymentRepository)

class AbstractUnitOfWork(Generic[T], abc.ABC):
    repo: AbstractPaymentRepository

    def __init__(self, repo: T):
        self.repo = repo

    @abc.abstractmethod
    async def __aenter__(self) -> 'AbstractUnitOfWork[T]':
        raise NotImplementedError
    
    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError
    
class SQLUnitOfWork(AbstractUnitOfWork[PaymentRepository]):
    def __init__(self, repo: PaymentRepository, session: AsyncSession):
        super().__init__(repo)
        self.session = session

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()
            await self.remove()
        
    async def remove(self):
        from app.setting.db import AsyncScopedSession

        await AsyncScopedSession.remove()