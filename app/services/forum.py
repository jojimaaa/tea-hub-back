from sqlalchemy import event
from app.models.forum import ForumPosts, ForumComments
import base36
from app.schemas.forum import *
from app.schemas.user import *
from app.models.forum import *
from app.models.user import *
from app.database import db_dependency
from fastapi import HTTPException, status
from app.services.auth import user_dependency


@event.listens_for(ForumPosts, "after_insert")
def generate_id36(mapper, connection, target):
    id36 = base36.dumps(target.id)
    connection.execute(
        ForumPosts.__table__.update()
        .where(ForumPosts.id == target.id)
        .values(id36=id36)
    )


@event.listens_for(ForumComments, "after_insert")
def generate_id36(mapper, connection, target):
    id36 = base36.dumps(target.id)
    connection.execute(
        ForumComments.__table__.update()
        .where(ForumComments.id == target.id)
        .values(id36=id36)
    )


def get_user(user_id: int, db: db_dependency) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST, details="User not found."
        )
    return user


def get_user_dto(user: user_dependency) -> UserDTO:
    user_dto = UserDTO(username=user.username, name=user.name)
    return user_dto


def get_op_user_dto_by_id(user_id: int, db: db_dependency) -> UserDTO:
    try:
        op_user = get_user(user_id, db)
        op_user_dto = get_user_dto(op_user)
    except Exception:
        op_user_dto = UserDTO(username="", name="Usuário deletado")
    return op_user_dto

def get_op_user_dto(user :user_dependency) -> UserDTO:
    try:
        op_user_dto = get_user_dto(user)
    except Exception:
        op_user_dto = UserDTO(username="", name="Usuário deletado")
    return op_user_dto


def get_topic(topic_id: int, db: db_dependency) -> ForumTopics:
    topic = db.query(ForumTopics).filter(ForumTopics.id == topic_id).first()
    if topic is None:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST, detail="Topic not found."
        )
    return topic


def get_topic_dto(topic: ForumTopics) -> ForumTopicOut:
    topic_dto = ForumTopicOut(id=topic.id, name=topic.name)
    return topic_dto


def get_post(post_id: int, db: db_dependency) -> ForumPosts:
    post = db.query(ForumPosts).filter(ForumPosts.id == post_id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    return post


def get_post_dto(
    post: ForumPosts, db: db_dependency, req_user : User | None = None
) -> ForumTopicOut:
    
    user = db.query(User).filter(User.id == post.user_id).first()

    likedByMe = False

    print(req_user)
    print(user)
    
    if(req_user is not None): likedByMe = get_liked_by_me(req_user.id, post.id, ForumPostLikes, ForumPostLikes.post_id, db)


    post_dto = ForumPostOut(
        id=base36.dumps(post.id),
        title=post.title,
        body=post.body,
        topic=get_topic_dto(get_topic(post.topic_id, db)),
        user=get_op_user_dto(user),
        created_at=post.created_at,
        comments=get_post_comments(post.id, db, req_user),
        like_count=post.like_count,
        liked_by_me= likedByMe,
    )
    return post_dto


def get_comment(comment_id: int, db: db_dependency) -> ForumComments:
    comment = db.query(ForumComments).filter(ForumComments.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Comment not found."
        )
    return comment


def get_comment_dto(
    comment: ForumComments, db: db_dependency, req_user : User | None = None
) -> ForumCommentOut:
    
    likedByMe = False
    
    if(req_user is not None): likedByMe = get_liked_by_me(req_user.id, comment.id, ForumCommentLikes, ForumCommentLikes.comment_id, db)

    comment_out = ForumCommentOut(
        id=base36.dumps(comment.id),
        body=comment.body,
        user=get_op_user_dto_by_id(comment.user_id, db),
        post_id=base36.dumps(comment.post_id),
        parent_id=base36.dumps(comment.parent_id) if comment.parent_id else None,
        created_at=comment.created_at,
        like_count=comment.like_count,
        liked_by_me=likedByMe,
    )
    return comment_out


def get_post_comments(post_id: int, db: db_dependency, req_user : User | None = None):
    comments = (
        db.query(ForumComments)
        .filter(ForumComments.post_id == post_id)
        .order_by(ForumComments.created_at)
        .all()
    )

    dtos = []
    for comment in comments:
        dtos.append(get_comment_dto(comment, db, req_user))

    return dtos


def get_sub_comments(
    comment_id: int, db: db_dependency, req_user : User | None = None
) -> list[ForumCommentOut]:
    comments = (
        db.query(ForumComments).filter(ForumComments.parent_id == comment_id).all()
    )

    comments_out: list[ForumCommentOut] = []

    for comment in comments:
        comments_out.append(get_comment_dto(comment, db, req_user))

    return comments_out


def get_liked_by_me(user_id: int, id: int, Model, field, db: db_dependency) -> bool:
    return (
        db.query(Model).filter((field == id) & (Model.user_id == user_id)).first()
        is not None
    )


def get_like(user_id: int, id: int, Model, field, db: db_dependency):
    return db.query(Model).filter((field == id) & (Model.user_id == user_id)).first()
