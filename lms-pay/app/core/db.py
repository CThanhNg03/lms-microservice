from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncIterator
import logging

from .setting import env

DATABASE_URL = env.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db() -> AsyncIterator[AsyncSession]:
    try:
        async with async_session() as session:
            yield session
    except SQLAlchemyError as e:
        logging.exception(e)
