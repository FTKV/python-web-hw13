from datetime import datetime, timezone
import pickle

from libgravatar import Gravatar
from sqlalchemy import select

from src.database.connect_db import AsyncDBSession, redis_db1
from src.database.models import User
from src.schemas.users import UserModel


async def set_user_in_cache(user) -> None:
    await redis_db1.set(f"user: {user.email}", pickle.dumps(user))
    await redis_db1.expire(f"user: {user.email}", 3600)


async def get_user_by_email_from_cache(email: str) -> User | None:
    user = await redis_db1.get(f"user: {email}")
    if user:
        return pickle.loads(user)


async def get_user_by_email(email: str, session: AsyncDBSession) -> User | None:
    stmt = select(User).filter(User.email == email)
    user = await session.execute(stmt)
    return user.scalar()


async def create_user(body: UserModel, session: AsyncDBSession) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception:
        pass
    user = User(**body.model_dump(), avatar=avatar)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await set_user_in_cache(user)
    return user


async def update_token(user: User, token: str | None, session: AsyncDBSession) -> None:
    user.refresh_token = token
    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await set_user_in_cache(user)


async def confirm_email(email: str, session: AsyncDBSession) -> None:
    user = await get_user_by_email(email, session)
    user.is_email_confirmed = True
    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await set_user_in_cache(user)


async def invalidate_password(email, session: AsyncDBSession) -> None:
    user = await get_user_by_email(email, session)
    user.is_password_valid = False
    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await set_user_in_cache(user)


async def reset_password(email, password, session: AsyncDBSession) -> None:
    user = await get_user_by_email(email, session)
    user.password = password
    user.is_password_valid = True
    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await set_user_in_cache(user)


async def update_avatar(email, url: str, session: AsyncDBSession) -> User:
    user = await get_user_by_email(email, session)
    user.avatar = url
    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await set_user_in_cache(user)
    return user
