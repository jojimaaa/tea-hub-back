from fastapi import APIRouter, HTTPException, status
from app.database import db_dependency
from app.services.auth import user_dependency
from app.schemas.forum import *
from app.services.forum import *
from app.models.forum import *
from app.models.user import *
from app.utils import normalize, search_by_title
from datetime import timedelta
import base36

router = APIRouter(prefix="/forum", tags=["Fórum"])


# ---------------- TOPICS ----------------


@router.get("/topics", response_model=list[ForumTopicOut])
async def get_topics(db: db_dependency) -> list[ForumTopicOut]:
    topics = db.query(ForumTopics).all()
    topics_out: list[ForumTopicOut] = []
    for topic in topics:
        topics_out.append(get_topic_dto(topic))
    return topics_out


@router.post("/topics")
async def create_topic(topic: ForumTopicSchema, db: db_dependency):
    new_topic = ForumTopics(name=topic.name, normalized_name=normalize(topic.name))
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    topic_out = get_topic_dto(new_topic)
    return topic_out


@router.patch("/topics/{topic_id}", response_model=ForumTopicOut)
async def update_topic(topic_id: int, data: ForumTopicSchema, db: db_dependency):
    topic = get_topic(topic_id, db)
    if data.name is not None:
        topic.name = data.name
        topic.normalized_name = normalize(data.name)
    db.commit()
    db.refresh(topic)

    topic_out = get_topic_dto(topic)
    return topic_out


@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int, db: db_dependency):
    topic = get_topic(topic_id, db)
    db.delete(topic)
    db.commit()
    return {"message": f"Tópico {topic.name}"}


# ---------------- POSTS ----------------


@router.get("/post/{post_id36}", response_model=ForumPostOut)
async def get_forum_post(post_id36: str, user: user_dependency, db: db_dependency):
    post_id = base36.loads(post_id36)
    post = get_post(post_id, db)
    post_out = get_post_dto(user, post, db)

    return post_out


@router.get("/search", response_model=list[ForumPostOut])
async def search_forum_post(
    db: db_dependency,
    user: user_dependency,
    topic_id: str | None = None,
    created_from: datetime | None = None,
    username: str | None = None,
    title: str | None = None,
):
    posts_query = db.query(ForumPosts)
    filters = []

    if topic_id is not None:
        filters.append(ForumPosts.topic_id == topic_id)
    if created_from is not None:
        filters.append(ForumPosts.created_at >= created_from)
    if username is not None:
        user = db.query(User).filter(User.username == username).first()
        filters.append(ForumPosts.user_id == user.id)
    if filters:
        posts_query = posts_query.filter(*filters)
    posts = posts_query.all()

    if title is not None:
        posts = search_by_title(title, posts, amount=15)

    posts_out = []
    for post in posts:
        posts_out.append(get_post_dto(user, post, db))

    return posts_out


@router.post("/submit", response_model=ForumPostOut)
async def submit_forum_post(
    user: user_dependency, post: ForumPostCreate, db: db_dependency
):

    new_post = ForumPosts(
        title=post.title, body=post.body, user_id=user.id, topic_id=post.topic_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    post_out = get_post_dto(user, new_post, db)

    return post_out


@router.patch("/post/{post_id36}", response_model=ForumPostOut)
async def edit_forum_post(
    user: user_dependency, post_id36: str, data: ForumPostUpdate, db: db_dependency
):
    post_id = base36.loads(post_id36)

    post: ForumPosts = get_post(post_id, db)

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ser autor do post para poder editar",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    post_out = get_post_dto(user, post, db)

    return post_out


@router.delete("/post/{post_id36}")
async def delete_post(user: user_dependency, post_id36: str, db: db_dependency):
    post_id = base36.loads(post_id36)

    post = get_post(post_id, db)

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ser autor do post para poder deletar",
        )

    db.delete(post)
    db.commit()
    return {"message": "Post deletado"}


# ---------------- COMMENTS ----------------


@router.get("/post/{post_id36}/comments", response_model=list[ForumCommentOut])
async def get_comments_endpoint(
    post_id36: str, user: user_dependency, db: db_dependency
):
    post_id = base36.loads(post_id36)

    comments = get_post_comments(user, post_id, db)

    return comments


@router.get("/post/{post_id36}/comment/{comment_id36}", response_model=ForumCommentOut)
async def get_comment_endpoint(
    comment_id36: str, user: user_dependency, db: db_dependency
):
    comment_id = base36.loads(comment_id36)
    return get_comment_dto(user, get_comment(comment_id, db), db)


@router.post("/post/{post_id36}/comment", response_model=ForumCommentOut)
async def submit_comment(
    post_id36: str,
    comment: ForumCommentCreate,
    user: user_dependency,
    db: db_dependency,
):
    post_id = base36.loads(post_id36)

    new_comment = ForumComments(
        body=comment.body,
        user_id=user.id,
        post_id=post_id,
        parent_id=base36.loads(comment.parent_id) if comment.parent_id else None,
        like_count=0,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    comment_out = get_comment_dto(user, new_comment, db)

    return comment_out


@router.patch(
    "/post/{post_id36}/comment/{comment_id36}", response_model=ForumCommentOut
)
async def edit_comment(
    edited_comment: ForumCommentUpdate,
    comment_id36: str,
    user: user_dependency,
    db: db_dependency,
):
    comment_id = base36.loads(comment_id36)

    comment = get_comment(comment_id, db)

    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Somente o autor do comentário tem permissão de edição",
        )

    updates = edited_comment.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)

    comment_out = get_comment_dto(user, comment, db)

    return comment_out


@router.delete("/post/{post_id36}/comment/{comment_id36}")
async def delete_comment(comment_id36: str, user: user_dependency, db: db_dependency):
    comment_id = base36.loads(comment_id36)

    comment = get_comment(comment_id, db)

    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Somente o autor do comentário tem permissão de edição",
        )

    db.delete(comment)
    db.commit()
    return {"message": "Comentário apagado."}


# ---------------------- LIKES -------------------------


@router.post("/post/{post_id36}/like", response_model=PostLikeOut)
async def toggle_post_like(post_id36: str, user: user_dependency, db: db_dependency):

    post_id = base36.loads(post_id36)

    like_out = PostLikeOut(post_id=post_id36, username=user.username, liked_by_me=False)

    like = get_like(user.id, post_id, ForumPostLikes, ForumPostLikes.post_id, db)

    if like is None:
        new_like = ForumPostLikes(
            post_id=post_id,
            user_id=user.id,
        )
        db.add(new_like)
        db.query(ForumPosts).filter(ForumPosts.id == post_id).update(
            {ForumPosts.like_count: ForumPosts.like_count + 1}
        )
        like_out.liked_by_me = True

    else:
        db.delete(like)
        db.query(ForumPosts).filter(ForumPosts.id == post_id).update(
            {ForumPosts.like_count: ForumPosts.like_count - 1}
        )

    db.commit()

    return like_out


@router.post(
    "/post/{post_id36}/comment/{comment_id36}/like", response_model=CommentLikeOut
)
async def toggle_comment_like(
    comment_id36: str, user: user_dependency, db: db_dependency
):

    comment_id = base36.loads(comment_id36)

    like_out = CommentLikeOut(
        comment_id=comment_id36, username=user.username, liked_by_me=False
    )

    like = get_like(
        user.id, comment_id, ForumCommentLikes, ForumCommentLikes.comment_id, db
    )

    if like is None:
        new_like = ForumCommentLikes(
            comment_id=comment_id,
            user_id=user.id,
        )
        db.add(new_like)
        db.query(ForumComments).filter(ForumComments.id == comment_id).update(
            {ForumComments.like_count: ForumComments.like_count + 1}
        )
        like_out.liked_by_me = True

    else:
        db.delete(like)
        db.query(ForumComments).filter(ForumComments.id == comment_id).update(
            {ForumComments.like_count: ForumComments.like_count - 1}
        )

    db.commit()

    return like_out
