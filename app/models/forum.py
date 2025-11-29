from sqlalchemy import (
    Column, Integer, String, Text, DateTime
)
from datetime import datetime, timezone
from app.database import Base

class ForumPosts(Base):
    __tablename__ = 'tb_forum_posts'
    
    id = Column(Integer, primary_key=True)
    id36 = Column(String(255), unique=True)
    title = Column(String(255))
    body = Column(Text)
    topic_id = Column(Integer)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    like_count = Column(Integer, default = 0)
    
class ForumTopics(Base):
    __tablename__ = 'tb_forum_topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    normalized_name = Column(String(255), unique=True)
    
class ForumComments(Base):
    __tablename__ = 'tb_comments'
    
    id = Column(Integer, primary_key=True)
    id36 = Column(String(255), unique=True)
    body = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer)
    post_id = Column(Integer)
    parent_id = Column(Integer, nullable=True)
    like_count = Column(Integer, default = 0)
    
class ForumPostLikes(Base):
    __tablename__ = 'tb_post_likes'
    
    user_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, primary_key=True)  
    
class ForumCommentLikes(Base):
    __tablename__ = 'tb_comment_likes'
    
    user_id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, primary_key=True)  