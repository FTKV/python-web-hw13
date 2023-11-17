from datetime import datetime, date

from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Boolean, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=True, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True, unique=True)
    birthday: Mapped[date] = mapped_column(Date())
    address: Mapped[str] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", onupdate="CASCADE")
    )
    user: Mapped["User"] = relationship("User", back_populates="contacts")

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_password_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    contacts: Mapped["Contact"] = relationship("Contact", back_populates="user")
