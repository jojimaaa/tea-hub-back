from sqlalchemy import UUID, Boolean, Column, ForeignKey, Integer, String, Text, DateTime
import uuid
from datetime import datetime
from .database import Base

class WikiPosts(Base):
    __tablename__ = 'tb_wiki_posts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author_name = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    topic_id = Column(UUID(as_uuid=True), nullable=False)
    
class User(Base):
    __tablename__ = 'tb_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    username = Column(String(255))
    email = Column(String(255))
    fl_admin = Column(Boolean)
    passwordhash = Column(String(255))