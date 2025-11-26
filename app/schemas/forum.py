from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# -------- DTOs --------

class ForumTopicDTO(BaseModel):
    id: str
    name: str

class UserDTO(BaseModel):
    username: str
    name: str

class IComment(BaseModel):
    id: str
    body: str
    user: UserDTO
    post_id: str
    parent_id: str | None
    created_at: datetime | str

class ForumCommentDTO (IComment):
    like_count: int #count das linhas de tb_comment_likes cujo id do comentário seja aquele fornecido
    liked_by_me: bool #verificar se id do usuário está presente na tabela SELECT (*) from tb_comment_likes WHERE comment_id ==:$comment_i

class ForumPostDTO (BaseModel):
    id: str
    title: str
    body: str
    topic: ForumTopicDTO
    user: UserDTO
    created_at: datetime | str
    comments: list[ForumCommentDTO] #lista de comentários do post nos moldes de ForumCommentDTO

# ---------- POSTS ----------
class ForumPostCreate(BaseModel):
    title: str
    body: str

class ForumPostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    topic: Optional[str] = None
  
class ForumPostOut (ForumPostDTO):
    like_count: int
    liked_by_me: bool

# ---------- TOPICS ----------    
class ForumTopicSchema(BaseModel):
    name: str
    
class ForumTopicOut(BaseModel):
    id: str
    name: str

# ---------- COMMENTS ---------- 
class ForumCommentCreate(BaseModel):
    body: str
    post_id: str
    username: str
    parent_id: str | None = None

class ForumCommentUpdate(BaseModel):            
    body: str
    username: str
    
class ForumCommentOut(ForumCommentDTO):
    comments: list[ForumCommentDTO]

# ---------- LIKES ----------

class CommentLikeSchema(BaseModel):
    comment_id: str
    username: str
    
class CommentLikeOut(CommentLikeSchema):
    liked_by_me: bool

class PostLikeSchema(BaseModel):
    post_id: str
    username: str
    
class PostLikeOut(PostLikeSchema):
    liked_by_me: bool