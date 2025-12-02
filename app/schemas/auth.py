from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


# ---------- LOGIN ----------
class LoginSchema(BaseModel):
    email: str
    password: str


# ---------- TOKEN ----------
class TokenSchema(BaseModel):
    username: str
    name: str
    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str

    model_config = {"from_attributes": True}
