from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)

from src.conf.config import settings


engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_url_async,
    echo=False,
)
AsyncDBSession = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


# Dependency
async def get_session():
    session = AsyncDBSession()
    try:
        yield session
    finally:
        await session.close()
