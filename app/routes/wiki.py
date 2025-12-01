from fastapi import HTTPException, APIRouter, status, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from app.database import db_dependency
from app.services.wiki import *
from app.schemas.wiki import *
from app.models.wiki import *
from datetime import datetime
from app.utils import normalize, search_by_title
from app.services.cloudinary import upload_image_to_cloudinary
from datetime import timedelta
from sqlalchemy import func
from random import randint

router = APIRouter(prefix="/wiki", tags=["Wiki"])


# ------------------- TOPICS --------------------


@router.get("/topics", response_model=list[WikiTopicOut])
async def get_wiki_topics(db: db_dependency):
    topics = db.query(WikiTopics).all()
    topics_out = []
    for topic in topics:
        topics_out.append(get_topic_dto(topic))
    return topics_out


@router.post("/topics", response_model=WikiTopicOut)
async def create_topic(topic: WikiTopicCreate, db: db_dependency):
    check_for_topic_name(topic.name, db)

    new_topic = WikiTopics(name=topic.name)

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    topic_out = get_topic_dto(new_topic)

    return topic_out


@router.patch("/topics/{topic_id}", response_model=WikiTopicOut)
async def edit_topic(topic_id: int, data: WikiTopicCreate, db: db_dependency):
    topic = get_topic(topic_id, db)

    check_for_topic_name(data.name, db)

    topic.name = data.name
    db.commit()
    db.refresh(topic)

    topic_out = get_topic_dto(topic)

    return topic_out


@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int, db: db_dependency):
    topic = get_topic(topic_id, db)
    db.delete(topic)
    db.commit()
    return {"message": f'Topic "{topic.name}" deleted.'}


# ------------------- POSTS --------------------


@router.get("/search", response_model=list[WikiPostOut])
async def search_posts(
    db: db_dependency,
    topic_id: int | None = None,
    created_from: datetime | None = None,
    author_name: str | None = None,
    title: str | None = None,
):
    filters = []

    if topic_id is not None:
        filters.append(WikiPosts.topic_id == topic_id)
    if created_from is not None:
        filters.append(WikiPosts.created_date >= created_from)
    if author_name is not None:
        filters.append(WikiPosts.author_name == author_name)

    posts_query = db.query(WikiPosts)

    if filters:
        posts_query = posts_query.filter(*filters)

    posts = posts_query.all()

    if title is not None:
        posts = search_by_title(title, posts)

    posts_out = []

    for post in posts:
        post_out = get_post_dto(post, db)
        posts_out.append(post_out)

    return posts_out


@router.get("/recommended", response_model=list[WikiPostOut])
async def get_recommended_posts(db: db_dependency):
    min_id, max_id = db.query(func.min(WikiPosts.id), func.max(WikiPosts.id)).first()

    if min_id is None:
        return []

    total_posts = db.query(func.count(WikiPosts.id)).scalar()

    limit = min(4, total_posts)

    posts_out: list[WikiPostOut] = []

    taken_ids = set()

    while len(posts_out) < limit:
        random_id = randint(min_id, max_id)
        if random_id in taken_ids:
            continue
        try:
            post = get_post(random_id, db)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                continue
            raise
        if post is not None:
            taken_ids.add(random_id)
            posts_out.append(get_post_dto(post, db))

    return posts_out


@router.get("/recent", response_model=list[WikiPostOut])
async def get_recent_posts(db: db_dependency):
    posts = db.query(WikiPosts).order_by(WikiPosts.created_date.desc()).limit(4).all()
    posts_out: list[WikiPostOut] = []
    for post in posts:
        post_out = get_post_dto(post, db)
        posts_out.append(post_out)
    return posts_out


@router.patch("/edit/{id}", response_model=WikiPostOut)
async def edit_wiki_post(
    id: int,
    db: db_dependency,
    title: str | None = Form(None),
    body: str | None = Form(None),
    author_name: str | None = Form(None),
    topic_id: str | None = Form(None),
    image: UploadFile | None = File(None)
):
    post = get_post(id, db)

    def valid(value):
        return value not in (None, "")

    if valid(title):
        check_for_title(title)
        post.title = title
        post.normalized_title = normalize(title)

    if valid(body):
        post.body = body

    if valid(author_name):
        post.author_name = author_name

    if valid(topic_id):
        post.topic_id = int(topic_id)

    if image is not None:
        post.image_url = await upload_image_to_cloudinary(image)

    db.commit()
    db.refresh(post)

    return get_post_dto(post, db)


@router.post("/upload-wiki-post", response_model=WikiPostOut)
async def create_wiki_post(
    title: str,
    body: str,
    author_name: str,
    topic_id: str,
    db: db_dependency,
    image: UploadFile = File(...),
):
    topic = get_topic(topic_id, db)
    image_url = await upload_image_to_cloudinary(image)

    check_for_title(title, db)

    new_post = WikiPosts(
        title=title,
        normalized_title=normalize(title),
        body=body,
        author_name=author_name,
        created_date=datetime.now(),
        topic_id=topic.id,
        image_url=image_url,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    post_out = get_post_dto(new_post, db)

    return post_out


@router.delete("/{id}")
async def delete_wiki_post(id: int, db: db_dependency):
    post = get_post(id, db)

    db.delete(post)
    db.commit()
    return {"message": f'Post "{post.title}" deleted.'}


@router.get("/{id}", response_model=WikiPostOut)
async def get_wiki_post(id: int, db: db_dependency):

    post = get_post(id, db)

    post_out = get_post_dto(post, db)

    return post_out
