from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, UUID4


class ContactModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=254)
    last_name: str = Field(min_length=2, max_length=254)
    email: EmailStr
    phone: str = Field(max_length=38)
    birthday: date
    address: str = Field(max_length=254)


class ContactResponse(ContactModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    user_id: UUID4

    class Config:
        from_attributes = True
