from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

class LoginBase(BaseModel):
    id: UUID
    name: str
    username: str
    email: str
    fl_admin: str
    passwordhash: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class WikiBase(BaseModel):
    title: str
    body: str
    author_name: str
    topic_id: UUID

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str

    model_config = {
        "from_attributes": True
    }