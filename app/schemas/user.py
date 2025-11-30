from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

# ---------- REGISTER ----------
class UserSchema(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str