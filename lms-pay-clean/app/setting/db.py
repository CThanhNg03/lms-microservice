from asyncio import current_task
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncIterator

from app.repositories.orm.admin import Admin
from app.setting.security import get_password_hash

from .setting import settings, logger

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

AsyncScopedSession = async_scoped_session(async_session, scopefunc=current_task)

def get_session() -> AsyncSession:
    return AsyncScopedSession()

async def initialize_db():
    async with engine.begin() as conn:
        user = settings.admin
        stmt = select(Admin).where(Admin.username == user["username"])
        
        try:
            result = await conn.execute(stmt)
            admin_user = result.fetchone()
            
            if not admin_user:
                stmt = insert(Admin).values(
                    username=user["username"],
                    email=user["email"],
                    password=get_password_hash(user["password"]),
                    is_active=True,
                    is_superuser=True
                )
                await conn.execute(stmt)
                await conn.commit()
                logger.info("Admin user created successfully.")
            else:
                logger.info("Admin user already exists.")
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {e}")
