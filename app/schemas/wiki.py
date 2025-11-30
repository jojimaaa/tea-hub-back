from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

# ---------- POSTS ----------
class WikiPostSchema(BaseModel):
    title: str
    body: str
    author_name: str
    topic_id: str
    image_url: str
    model_config = {
        "from_attributes": True
    }    
    
class WikiPostUpdateSchema(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    author_name: Optional[str] = None
    topic_id: Optional[int] = None    
    image_url: Optional[UploadFile] = None
    
# ---------- TOPICS ----------    
class WikiTopicSchema(BaseModel):
    name: str
    
    model_config = {
        "from_attributes": True
    }    