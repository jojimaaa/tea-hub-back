from fastapi import HTTPException, APIRouter, status, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from app.database import db_dependency
from app.schemas.wiki import *
from app.models.wiki import *
from datetime import datetime
from app.utils import normalize, search_by_title
from app.services.cloudinary import upload_image_to_cloudinary
from datetime import timedelta

router = APIRouter(prefix="/wiki", tags=["Wiki"])

@router.get("/topics")
async def get_wiki_topics(db: db_dependency):
    topics = [name for (name,) in db.query(WikiTopics.name).all()]
    return topics

@router.post("/topics", response_model=WikiTopicSchema)
async def create_topic(topic: WikiTopicSchema, db: db_dependency):
    new_topic = WikiTopics(
        name = topic.name
    )
    
    if (db.query(WikiTopics).filter(WikiTopics.name == new_topic.name).first()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tópico já existe"
        )

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

@router.patch("/topics/{topic_id}", response_model=WikiPostSchema)
async def edit_topic(topic_id: int, new_name: str, db: db_dependency):
    topic = db.query(WikiTopics).filter(WikiTopics.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if new_name is not None:
        topic.name = new_name
    
    topic.name = new_name
    db.commit()
    db.refresh(topic)
    return topic

@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int, db: db_dependency):
    topic = db.query(WikiTopics).filter(WikiTopics.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(topic)
    db.commit()
    return {"message": f"Tópico \"{topic.name}\" deletado."}

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
        filters.append(WikiPosts.topic_id == topic_id)
    if created_date is not None:
        next_day = created_date + timedelta(days=1)
        filters.append(WikiPosts.created_date >= created_date)
        filters.append(WikiPosts.created_date < next_day)
    if author_name is not None:
        filters.append(WikiPosts.author_name == author_name)
        
    posts_query = db.query(WikiPosts)
    
    if filters:
        posts_query = posts_query.filter(*filters)

    posts = posts_query.all()

    if title is not None:
        posts = search_by_title(title, posts, amount=15)

    return posts

@router.get("/recommended")
async def get_recommended_posts(db: db_dependency):
    posts = (
        db.query(WikiPosts)
        .order_by(WikiPosts.created_date.desc())
        .limit(4)
        .all()
    )
    return posts    

@router.patch("/edit/{title}", response_model=WikiPostSchema)
async def edit_wiki_post(
    db: db_dependency, 
    title: str,
    data: WikiPostUpdateSchema
):
    post = (
        db.query(WikiPosts)
        .filter(WikiPosts.normalized_title == title)
        .first()
    )
    
    if not post:
        raise HTTPException(404, "Post não encontrado")
    
    if db.query(WikiPosts).filter(WikiPosts.title == data.title).first() is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, message="This title already exists!")

    for attr, value in data.model_dump(exclude_unset=True).items():
        if attr == "title":
            post.title = value
            post.normalized_title = normalize(value)
        else:
            setattr(post, attr, value)

    if data.image_url is not None:
        post.image_url = await upload_image_to_cloudinary(data.image_url)

    db.commit()
    db.refresh(post)

    return post

@router.post("/upload-wiki-post", response_model=WikiPostSchema)
async def create_wiki_post(    
    title: str,
    body: str,
    author_name: str,
    topic_id: str,
    db: db_dependency,
    image: UploadFile = File(...)
):
    topic = db.query(WikiTopics).filter(WikiTopics.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This topic does not exists')    
    
    image_url = await upload_image_to_cloudinary(image)
    
    new_post = WikiPosts(
        title=title,
        normalized_title=normalize(title),
        body=body,
        author_name=author_name,
        created_date=datetime.now(),
        topic_id=topic_id,
        image_url = image_url
    )
    
    if (db.query(WikiPosts).filter(WikiPosts.normalized_title == new_post.normalized_title).first()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This title already exists')
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{post_id}")
async def delete_wiki_post(post_id: int, db: db_dependency):
    post = db.query(WikiPosts).filter(WikiPosts.id == post_id).first()
    if post_id is None:
        raise HTTPException(status_code=404, detail="Wiki post not found")

    db.delete(post)
    db.commit()
    return {"message": f"Tópico \"{post.name}\" deletado."}

@router.get("/{title}", response_model=WikiPostSchema)
async def get_wiki_post(title: str, db: db_dependency):
    
    title_formatted = normalize(title)
    
    post = db.query(WikiPosts).filter(WikiPosts.normalized_title == title_formatted).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Wiki Post not found')   
    
    if (post.normalized_title != title):
        canonical_url = f"/wiki/{title_formatted}"
        return RedirectResponse(url=canonical_url, status_code=301)

    return post