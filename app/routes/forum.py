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

# ---------------- POSTS ----------------

@router.get("/{topic}/{post_id36}")
async def get_forum_post(post_id36: str, db: db_dependency):
    post_id = base36.loads(post_id36)
    post = db.query(ForumPosts).filter(ForumPosts.id == post_id).first()
    return post

@router.get("/search/")
async def search_forum_post(
    db: db_dependency,
    topic_id: str | None = None, 
    created_at: datetime | None = None,
    username: str | None = None,
    title: str | None = None
):
    filters = []
    
    if topic_id is not None:
        filters.append(ForumPosts.topic_id == topic_id)
    if created_at is not None:
        next_day = created_at + timedelta(days=1)
        filters.append(ForumPosts.created_at >= created_at)
        filters.append(ForumPosts.created_at < next_day)
    if username is not None:
        user = db.query(User).filter(User.username == username).first()
        filters.append(ForumPosts.user_id == user.id)
        
    posts_query = db.query(ForumPosts)
    
    if filters:
        posts_query = posts_query.filter(*filters)

    posts = posts_query.all()

    if title is not None:
        posts = search_by_title(title, posts, amount=15)
        
    return posts

@router.post("/{topic}/submit/")
async def submit_forum_post(user: user_dependency, topic: str, post: ForumPostCreate, db: db_dependency):
    topic_id = db.query(ForumTopics).filter(ForumTopics.normalized_name == topic).first().id
    
    if topic_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="Topic not found.")
    
    new_post = ForumPosts(
        title = post.title,
        body = post.body,
        user_id = user.id,
        topic_id = topic_id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.patch("/{topic}/{post_id36}")
async def edit_forum_post(
    user: user_dependency, 
    post_id36: str, 
    data: ForumPostUpdate,
    db: db_dependency
):
    post_id = base36.loads(post_id36)    
    
    post = db.query(ForumPosts).filter(ForumPosts.id == post_id).first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="Post not found")
    
    if (post.user_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ser autor do post para poder editar"
        )
    
    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(post, field, value)
        
    db.commit()
    db.refresh(post)
    return post
    
@router.delete("/{topic}/{post_id36}")
async def delete_post(
    user: user_dependency,
    post_id36: str,
    db: db_dependency
):
    post_id = base36.loads(post_id36)
    
    post = db.query(ForumPosts).filter(ForumPosts.id == post_id).first()
    
    if (post.user_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ser autor do post para poder deletar"
        )
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    return {"message": "Post deletado"}



# ---------------- TOPICS ----------------

@router.get("/topics")
async def get_topics(db: db_dependency) -> list[ForumTopicOut]:
    topics = db.query(ForumTopics.name).all()
    topics_out: list[ForumTopicOut] = []
    for topic in topics:
        topic_out = ForumTopicOut(
            id = topic.id,
            name = topic.name
        )
        topics_out.append(topic_out)
    return topics_out

@router.post("/topics")
async def create_topic(topic: ForumTopicSchema, db: db_dependency):
    new_topic = ForumTopics(
        name = topic.name,
        normalized_name = normalize(topic.name)
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    topic_out = ForumTopicOut(
        id = topic.id,
        name = topic.name
    )
    
    return topic_out

@router.patch("topics/{normalized_name}")
async def update_topic(normalized_name: str, data: ForumTopicSchema, db: db_dependency):
    topic = db.query(ForumTopics).filter(ForumTopics.normalized_name == normalized_name).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    if data.name is not None:
        topic.name = data.name
        topic.normalized_name = normalize(data.name)
    db.commit()
    db.refresh(topic)
    
    topic_out = ForumTopicOut(
        id = topic.id,
        name = topic.name
    )
    
    return topic_out

@router.delete("/topics/{normalized_name}")
async def delete_topic(normalized_name: str, db: db_dependency):
    topic = db.query(ForumTopics).filter(ForumTopics.normalized_name == normalized_name).first()
    db.delete(topic)
    db.commit()
    return {"message": f"Tópico {topic.name}"}





# ---------------- COMMENTS ----------------

@router.get("/{topic}/{post_id36}/comments")
async def get_post_comments(post_id36: str, db: db_dependency):
    post_id = base36.loads(post_id36)
    
    root_comments = (
        db.query(ForumComments)
          .filter(
              (ForumComments.post_id == post_id) &
              (ForumComments.parent_id == None)
          )
          .all()
    )
    
    if root_comments:
        print("tem algo")
    else:
        print("achei poha nenhuma")

    tree = []
    for comment in root_comments:
        user = db.query(User).filter(User.id == comment.user_id).first()

        user_dto = UserDTO(username=user.username, name=user.name)

        root_out = ForumCommentOut(
            id=base36.dumps(comment.id),
            body=comment.body,
            user=user_dto,
            post_id=base36.dumps(comment.post_id),
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            like_count=comment.like_count,
            liked_by_me=False,
            comments=get_comments(comment.id, db),
        )

        tree.append(root_out)

    return tree

@router.post("/{topic}/{post_id36}/comment")
async def submit_comment(post_id36: str, comment: ForumCommentCreate, user: user_dependency,db: db_dependency):
    post_id = base36.loads(post_id36)
    
    new_comment = ForumComments(
        body = comment.body,
        user_id = user.id,
        post_id = post_id,
        parent_id = base36.loads(comment.parent_id) if comment.parent_id else None,
        like_count = 0
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    user_dto = UserDTO (
        username = user.username,
        name = user.name
    )
    
    comment_out = ForumCommentOut (
        id = new_comment.id36,
        body = new_comment.body,
        user = user_dto,
        post_id = post_id36,
        parent_id = base36.dumps(new_comment.parent_id) if new_comment.parent_id else None,
        created_at = new_comment.created_at,
        like_count = new_comment.like_count,
        liked_by_me = False,
        comments = []
    )
    
    return comment_out
        
@router.patch("/{topic}/{post_id36}/comment/{comment_id36}")
async def edit_comment(edited_comment: ForumCommentUpdate,comment_id36: str, post_id36: str, user: user_dependency, db: db_dependency):
    post_id = base36.loads(post_id36)
    comment_id = base36.loads(comment_id36)
    
    comment = (
        db.query(ForumComments)
            .filter(
                ForumComments.id == comment_id,
                ForumComments.post_id == post_id
            )
            .first()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details="Comment not found.")
    
    if (comment.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Somente o autor do comentário tem permissão de edição")
    
    updates = edited_comment.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)
    
    user_dto = UserDTO(
        username = user.username,
        name = user.name
    )
    
    if (db.query(ForumCommentLikes)
            .filter((ForumCommentLikes.comment_id == comment_id) &
                    (ForumCommentLikes.user_id == user.id))
            .first()):
        liked_by_me = True
    else:
        liked_by_me = False
        
    
    comment_out = ForumCommentOut(
        id = base36.dumps(comment.id),
        body = comment.body,
        user = user_dto,
        post_id = base36.dumps(comment.post_id),
        parent_id = comment.parent_id,
        created_at = comment.created_at,
        like_count = comment.like_count,
        liked_by_me = liked_by_me,
        comments = get_comments(comment.id, db),
    )
    
    return comment_out

@router.delete("/{topic}/{post_id36}/comment/{comment_id36}")
async def delete_comment(post_id36: str, comment_id36: str, user: user_dependency, db: db_dependency):
    post_id = base36.loads(post_id36)
    comment_id = base36.loads(comment_id36)
    
    comment = (
        db.query(ForumComments)
            .filter(
                ForumComments.id == comment_id,
                ForumComments.post_id == post_id
            )
            .first()
        )
    
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado nesse post.")    
    
    if (comment.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Somente o autor do comentário tem permissão de edição")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comentário apagado."}


# ---------------------- LIKES -------------------------

@router.post("/{topic}/{post_id36}/like")
async def toggle_post_like(post_id36: str, user: user_dependency, db: db_dependency):
    
    post_id = base36.loads(post_id36)
    
    like_out = PostLikeOut(
        post_id = post_id36,
        username = user.username,
        liked_by_me = False
    )
    
    like = (db.query(ForumPostLikes)
        .filter(
            (ForumPostLikes.post_id == post_id) & 
            (ForumPostLikes.user_id == user.id)
        )
        .first()
    )
    
    if like is None:
        new_like = ForumPostLikes(
            post_id = post_id,
            user_id = user.id,
        )
        db.add(new_like)
        db.query(ForumPosts).filter(ForumPosts.id == post_id).update(
            {ForumPosts.like_count: ForumPosts.like_count + 1}
        )
        db.commit()
        like_out.liked_by_me = True
        
    else:
        db.delete(like)
        db.query(ForumPosts).filter(ForumPosts.id == post_id).update(
            {ForumPosts.like_count: ForumPosts.like_count - 1}
        )
        db.commit()

    return like_out

@router.post("/{topic}/{post_id36}/comment/{comment_id36}/like")
async def toggle_comment_like(comment_id36: str, user: user_dependency, db: db_dependency):
    
    comment_id = base36.loads(comment_id36)
    
    like_out = CommentLikeOut(
        comment_id = comment_id36,
        username = user.username,
        liked_by_me = False
    )
    
    like = (
        db.query(ForumCommentLikes)
            .filter((ForumCommentLikes.comment_id == comment_id) & 
                    (ForumCommentLikes.user_id == user.id)
                    )
            .first()
        )
    
    if like is None:
        new_like = ForumCommentLikes(
            comment_id = comment_id,
            user_id = user.id,
        )
        db.add(new_like)
        db.query(ForumComments).filter(ForumComments.id == comment_id).update(
            {ForumComments.like_count: ForumComments.like_count + 1}
        )
        db.commit()
        like_out.liked_by_me = True
        
    else:
        db.delete(like)
        
        db.query(ForumComments).filter(ForumComments.id == comment_id).update(
            {ForumComments.like_count: ForumComments.like_count - 1}
        )
        
        db.commit()

    return like_out