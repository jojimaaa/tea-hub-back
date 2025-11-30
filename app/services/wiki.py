from app.models.wiki import *
from app.schemas.wiki import *
from app.database import db_dependency
from fastapi import HTTPException, status


def get_topic(topic_id: int, db: db_dependency) -> WikiTopics:
    topic = db.query(WikiTopics).filter(WikiTopics.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found."
        )
    return topic


def get_topic_dto(topic: WikiTopics):
    topic_out = WikiTopicOut(id=topic.id, name=topic.name)
    return topic_out


def get_post(post_id: int, db: db_dependency) -> WikiPosts:
    post = db.query(WikiPosts).filter(WikiPosts.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wiki Post not found"
        )
    return post


def get_post_dto(post: WikiPosts, db: db_dependency):
    post_out = WikiPostOut(
        id=post.id,
        title=post.title,
        normalized_title=post.normalized_title,
        body=post.body,
        author_name=post.author_name,
        created_date=post.created_date,
        topic=get_topic_dto(get_topic(post.topic_id, db)),
        image_url=post.image_url,
    )
    return post_out


def check_for_title(normalized_title: str, db: db_dependency) -> None:
    if (
        db.query(WikiPosts)
        .filter(WikiPosts.normalized_title == normalized_title)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This title already exists."
        )


def check_for_topic_name(name: str, db: db_dependency) -> None:
    if db.query(WikiTopics).filter(WikiTopics.name == name).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This topic already exists."
        )
