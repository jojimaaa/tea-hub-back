from sqlalchemy import event
from sqlalchemy.orm import Mapper
from app.models.forum import ForumPosts, ForumComments
import base36
from app.schemas.forum import *
from app.schemas.user import *
from app.models.forum import *
from app.models.user import *
from app.database import db_dependency

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
    
    
def get_comments(id: int, db: db_dependency) -> list[ForumCommentOut]:
    comments = db.query(ForumComments).filter(ForumComments.parent_id == id).all()

    comments_out: list[ForumCommentOut] = []

    for comment in comments:
        
        user = db.query(User).filter(User.id == comment.user_id).first()
        
        user_dto = UserDTO(
            username = user.username,
            name = user.name
        )

        comment_out = ForumCommentOut(
                id = base36.dumps(comment.id),
                body = comment.body,
                user = user_dto,
                post_id = base36.dumps(comment.post_id),
                parent_id = base36.dumps(comment.parent_id),
                created_at = comment.created_at,
                like_count = comment.like_count,
                liked_by_me = False,
                comments = [] 
            )
        
        comment_out.comments = get_comments(comment.id, db)
        
        if (db.query(ForumPostLikes)
            .filter(
                (ForumPostLikes.post_id == comment.id) & 
                (ForumPostLikes.user_id == comment.user_id)
            )
            .first()
            is not None
        ):
            comment_out.liked_by_me = True
        
        comments_out.append(comment_out)
    return comments_out