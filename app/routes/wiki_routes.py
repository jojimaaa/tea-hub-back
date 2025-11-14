from fastapi import HTTPException, APIRouter, status, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from uuid import UUID
from app.database import db_dependency
from app import schemas, models
from datetime import datetime
from app.utils import normalize, search_by_title
from app.services.cloudinary_service import upload_image_to_cloudinary

router = APIRouter(prefix="/wiki", tags=["Wiki"])

@router.get("/topics")
async def get_wiki_topics(db: db_dependency):
    topics = [name for (name,) in db.query(models.WikiTopics.name).all()]
    return topics

@router.post("/topics/create_topic")
async def create_topic(topic: schemas.WikiTopicSchema, db: db_dependency):
    new_topic = models.WikiTopics(
        id = normalize(topic.name),
        name = topic.name
    )
    
    if (db.query(models.WikiTopics).filter(models.WikiTopics.id == new_topic.id).first()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tópico já existe"
        )

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

@router.get("/search")
async def get_wiki_post_list(
    db: db_dependency,
    topic_id: str | None = None, 
    created_date: datetime | None = None,
    author_name: str | None = None,
    title: str | None = None
):
    filters = []
    
    if topic_id is not None:
        filters.append(models.WikiPosts.topic_id == topic_id)
    if created_date is not None:
        filters.append(models.WikiPosts.created_date == created_date)
    if author_name is not None:
        filters.append(models.WikiPosts.author_name == author_name)
        
    posts_query = db.query(models.WikiPosts)
    
    if filters:
        posts_query = posts_query.filter(*filters)

    posts = posts_query.all()

    if title is not None:
        posts = search_by_title(title, posts, amount=15)

    return posts

@router.get("/recommended")
async def get_recommended_posts(db: db_dependency):
    posts = (
        db.query(models.WikiPosts)
        .order_by(models.WikiPosts.created_date.desc())
        .limit(4)
        .all()
    )
    return posts    

@router.patch("/edit/{wiki_title}")
async def edit_wiki_post(
    db: db_dependency, 
    wiki_title: str,
    body: str = Form(None),
    author_name: str = Form(None),
    topic_id: str = Form(None),
    image: UploadFile = File(None),    
):
    wiki_post = (
        db.query(models.WikiPosts)
        .filter(models.WikiPosts.normalized_title == wiki_title)
        .first()
    )
    
    if not wiki_post:
        raise HTTPException(404, "Post não encontrado")

    if wiki_title is not None and wiki_title != "":
        wiki_post.title = wiki_title
        wiki_post.normalized_title = normalize(wiki_title)
    if body is not None and body != "":
        wiki_post.body = body
    if author_name is not None and author_name != "":
        wiki_post.author_name = author_name
    if topic_id is not None and topic_id != "":
        wiki_post.topic_id = topic_id

    if image:
        wiki_post.image_url = await upload_image_to_cloudinary(image)

    db.commit()
    db.refresh(wiki_post)

    return wiki_post

@router.post("/upload-wiki-post")
async def make_wiki_post(    
    title: str,
    body: str,
    author_name: str,
    topic_id: str,
    db: db_dependency,
    image: UploadFile = File(...)
):
    topic = db.query(models.WikiTopics).filter(models.WikiTopics.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This topic does not exists')    
    
    image_url = await upload_image_to_cloudinary(image)
    
    new_post = models.WikiPosts(
        title=title,
        normalized_title=normalize(title),
        body=body,
        author_name=author_name,
        created_date=datetime.now(),
        topic_id=topic_id,
        image_url = image_url
    )
    
    if (db.query(models.WikiPosts).filter(models.WikiPosts.normalized_title == new_post.normalized_title).first()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This title already exists')
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{wiki_title}")
async def get_wiki_post(wiki_title: str, db: db_dependency):
    
    wiki_title_formatted = normalize(wiki_title)
    
    wiki_post = db.query(models.WikiPosts).filter(models.WikiPosts.normalized_title == wiki_title_formatted).first()
    
    if not wiki_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Wiki Post not found')   
    
    if (wiki_post.normalized_title != wiki_title):
        canonical_url = f"/wiki/{wiki_title_formatted}"
        return RedirectResponse(url=canonical_url, status_code=301)

    return wiki_post