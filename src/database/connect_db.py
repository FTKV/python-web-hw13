from fastapi import HTTPException, status
import redis.asyncio as redis
from sqlalchemy.exc import SQLAlchemyError
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
    except SQLAlchemyError as error_message:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(error_message)}",
        )
    finally:
        await session.close()


redis_db0 = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    password=settings.redis_password,
    encoding="utf-8",
    decode_responses=True,
)

redis_db1 = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=1,
    password=settings.redis_password,
    encoding="utf-8",
    decode_responses=False,
)
