from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=150)
    last_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(max_length=30)
    birthday: date
    address: str = Field(max_length=150)


class ContactResponse(ContactModel):
    id: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPasswordResetConfirmationModel(BaseModel):
    password_reset_confirmation_token: str


class RequestEmail(BaseModel):
    email: EmailStr
