from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, HttpUrl, UUID4


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=254)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserRequestEmail(BaseModel):
    email: EmailStr


class UserPasswordResetConfirmationModel(BaseModel):
    password: str = Field(min_length=8, max_length=72)


class UserDb(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    avatar: HttpUrl

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"
