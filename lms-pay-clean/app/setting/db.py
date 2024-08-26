from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncIterator

from .setting import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

AsyncScopedSession = async_scoped_session(async_session, scopefunc=current_task)

async def get_session() -> AsyncSession:
    return AsyncScopedSession()

