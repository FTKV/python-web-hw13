from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPasswordResetConfirmationModel(BaseModel):
    password_reset_confirmation_token: str
