from collections import defaultdict
from datetime import datetime, date, timedelta, timezone
from typing import List

from sqlalchemy import select, and_

from src.database.connect_db import AsyncDBSession
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel
from src.utils.is_leap_year import is_leap_year


async def read_contacts(
    offset: int,
    limit: int,
    first_name: str,
    last_name: str,
    email: str,
    user: User,
    session: AsyncDBSession,
) -> List[Contact] | None:
    stmt = select(Contact).filter(Contact.user_id == user.id)
    if first_name:
        stmt = stmt.filter(Contact.first_name.like(f"%{first_name}%"))
    if last_name:
        stmt = stmt.filter(Contact.last_name.like(f"%{last_name}%"))
    if email:
        stmt = stmt.filter(Contact.email.like(f"%{email}%"))
    stmt = stmt.offset(offset).limit(limit)
    contacts = await session.execute(stmt)
    return contacts.scalars()


async def read_contacts_with_birthdays_in_n_days(
    n: int,
    offset: int,
    limit: int,
    user: User,
    session: AsyncDBSession,
) -> List[Contact] | None:
    stmt = select(Contact).filter(Contact.user_id == user.id)
    contacts = await session.execute(stmt)
    contacts = contacts.scalars()
    tmp = defaultdict(list)
    today_date = date.today()
    is_leap_year_flag = is_leap_year(today_date.year)
    number_of_days_in_year = 365 + is_leap_year_flag
    last_date = today_date + timedelta(days=n - 1)
    is_includes_next_year_flag = bool(last_date.year - today_date.year)
    for contact in contacts:
        birthday = contact.birthday
        if not is_leap_year_flag and birthday.month == 2 and birthday.day == 29:
            date_delta = date(year=today_date.year, month=3, day=1) - today_date
        else:
            date_delta = birthday.replace(year=today_date.year) - today_date
        delta_days = date_delta.days
        if is_includes_next_year_flag and delta_days < n - number_of_days_in_year:
            delta_days += number_of_days_in_year
        if 0 <= delta_days < n:
            tmp[delta_days].append(contact)
    result = []
    for delta_days in range(n):
        result = result + tmp[delta_days]
    return result[offset : offset + limit]


async def read_contact(
    contact_id: int, user: User, session: AsyncDBSession
) -> Contact | None:
    stmt = select(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == user.id)
    )
    contact = await session.execute(stmt)
    return contact.scalar()


async def create_contact(
    body: ContactModel, user: User, session: AsyncDBSession
) -> Contact:
    try:
        contact = Contact(**body.model_dump(), user_id=user.id)
        session.add(contact)
        await session.commit()
        await session.refresh(contact)
    except Exception:
        return None
    return contact


async def update_contact(
    contact_id: int, body: ContactModel, user: User, session: AsyncDBSession
) -> Contact | None:
    stmt = select(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == user.id)
    )
    contact = await session.execute(stmt)
    contact = contact.scalar()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.address = body.address
        contact.updated_at = datetime.now(timezone.utc)
        await session.commit()
    return contact


async def delete_contact(
    contact_id: int, user: User, session: AsyncDBSession
) -> Contact | None:
    stmt = select(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == user.id)
    )
    contact = await session.execute(stmt)
    contact = contact.scalar()
    if contact:
        await session.delete(contact)
        await session.commit()
    return contact
