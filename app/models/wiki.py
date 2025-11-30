from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from app.database import Base


class WikiPosts(Base):
    __tablename__ = "tb_wiki_posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    normalized_title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author_name = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    topic_id = Column(Integer, ForeignKey("tb_wiki_topics.id"))
    image_url = Column(String(255))


class WikiTopics(Base):
    __tablename__ = "tb_wiki_topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
