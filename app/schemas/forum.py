from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserDTO(BaseModel):
    username: str
    name: str


# ---------- TOPICS ----------
class ForumTopicSchema(BaseModel):
    name: str


class ForumTopicOut(BaseModel):
    id: str
    name: str


# ---------- COMMENTS ----------
class ForumCommentCreate(BaseModel):
    body: str
    parent_id: str | None = None


class ForumCommentUpdate(BaseModel):
    body: str


class ForumCommentOut(BaseModel):
    id: str
    body: str
    user: UserDTO
    post_id: str
    parent_id: str | None
    created_at: datetime | str
    like_count: int
    liked_by_me: bool
    comments: list["ForumCommentOut"]


# ---------- POSTS ----------
class ForumPostCreate(BaseModel):
    title: str
    body: str
    topic_id: int


class ForumPostUpdate(BaseModel):
    title: Optional[str]
    body: Optional[str]


class ForumPostOut(BaseModel):
    id: str
    title: str
    body: str
    topic: ForumTopicOut
    user: UserDTO
    created_at: datetime | str
    comments: list[
        ForumCommentOut
    ]  # lista de comentários do post nos moldes de ForumCommentDTO
    like_count: int
    liked_by_me: bool


# ---------- LIKES ----------


class CommentLikeSchema(BaseModel):
    comment_id: str


class CommentLikeOut(CommentLikeSchema):
    liked_by_me: bool


class PostLikeSchema(BaseModel):
    post_id: str


class PostLikeOut(PostLikeSchema):
    liked_by_me: bool
