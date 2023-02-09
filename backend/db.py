from typing import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from config import settings


# https://github.com/tiangolo/sqlmodel/issues/189
Select.inherit_cache = True  # type: ignore
SelectOfScalar.inherit_cache = True  # type: ignore

engine = create_async_engine(
    settings.DATABASE_URL, echo=settings.DEBUG,
    pool_size=settings.POOL_SIZE, max_overflow=settings.MAX_OVERFLOW)

# https://github.com/tiangolo/sqlmodel/issues/54
SessionLocal = sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)  # type: ignore


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
