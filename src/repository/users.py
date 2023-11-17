from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, session: Session) -> User | None:
    stmt = select(User).filter(User.email == email)
    user = await session.execute(stmt)
    return user.scalar()


async def create_user(body: UserModel, session: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    user = User(**body.dict(), avatar=avatar)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_token(user: User, token: str | None, session: Session) -> None:
    user.refresh_token = token
    await session.commit()


async def confirm_email(email: str, session: Session) -> None:
    user = await get_user_by_email(email, session)
    user.is_email_confirmed = True
    await session.commit()


async def update_avatar(email, url: str, session: Session) -> User:
    user = await get_user_by_email(email, session)
    user.avatar = url
    await session.commit()
    return user


async def invalidate_password(email, session) -> None:
    user = await get_user_by_email(email, session)
    user.is_password_valid = False
    await session.commit()


async def reset_password(body: UserModel, session: Session) -> User:
    user = await get_user_by_email(body.email, session)
    user.password = body.password
    user.is_password_valid = True
    await session.commit()
    return user
