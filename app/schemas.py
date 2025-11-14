from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserSchema(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str
    
class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    
class WikiPostSchema(BaseModel):
    title: str
    body: str
    author_name: str
    topic_id: str
    image_url: str
    
class WikiTopicSchema(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: UUID
    email: str

    model_config = {
        "from_attributes": True
    }