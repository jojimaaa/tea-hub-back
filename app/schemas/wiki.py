from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile
from datetime import datetime


# ---------- TOPICS ----------
class WikiTopicCreate(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class WikiTopicOut(BaseModel):
    id: int
    name: str


# ---------- POSTS ----------
class WikiPostCreate(BaseModel):
    title: str
    body: str
    author_name: str
    topic_id: str
    image_url: str
    model_config = {"from_attributes": True}


class WikiPostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    author_name: Optional[str] = None
    topic_id: Optional[int] = None


class WikiPostOut(BaseModel):
    id: int
    title: str
    normalized_title: str
    body: str
    author_name: str
    created_date: datetime
    topic: WikiTopicOut
    image_url: str
