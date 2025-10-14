from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

from sqlalchemy import UUID
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

class WikiBase(BaseModel):
    id: UUID
    title: str
    body: str
    author_name: str
    created_date: datetime
    topic_id: UUID

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/wiki/{wiki_id}")
async def get_wiki_post(wiki_id: UUID, db: db_dependency):   
    wiki_post = db.query(models.WikiPosts).filter(models.WikiPosts.id == wiki_id).first()
    if not wiki_post:
        raise HTTPException(status_code=404, detail='Wiki Post not found')  
    return wiki_post
    