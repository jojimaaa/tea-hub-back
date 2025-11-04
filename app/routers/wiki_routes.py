from fastapi import HTTPException, APIRouter
from uuid import UUID
from app.database import db_dependency
from . import schemas, models

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/wiki/{wiki_id}")
async def get_wiki_post(wiki_id: UUID, db: db_dependency):
    wiki_post = db.query(models.WikiPosts).filter(models.WikiPosts.id == wiki_id).first()
    if not wiki_post:
        raise HTTPException(status_code=404, detail='Wiki Post not found')
    return wiki_post

@router.post("/wiki")
async def make_wiki_post(wiki_post: schemas.WikiBase, db: db_dependency):
    new_post = models.WikiPosts(
        id=wiki_post.id,
        title=wiki_post.title,
        body=wiki_post.body,
        author_name=wiki_post.author_name,
        created_date=wiki_post.created_date,
        topic_id=wiki_post.topic_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post