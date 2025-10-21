from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from uuid import UUID
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

from . import schemas, models, utils, auth

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

models.Base.metadata.create_all(bind=engine)

try:
    from .routers import data_routes
    app.include_router(data_routes.router, prefix="/data", tags=["dados"])
except Exception as e:
    print(f"[main] Aviso: router de dados não incluído: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/wiki/{wiki_id}")
async def get_wiki_post(wiki_id: UUID, db: db_dependency):
    wiki_post = db.query(models.WikiPosts).filter(models.WikiPosts.id == wiki_id).first()
    if not wiki_post:
        raise HTTPException(status_code=404, detail='Wiki Post not found')
    return wiki_post

@app.post("/wiki")
async def make_wiki_post(wiki_post: schemas.WikiBase, db: db_dependency):
    new_post = models.WikiPosts(
        id=wiki_post.id,
        title=wiki_post.title,
        body=wiki_post.body,
        author_name=wiki_post.author_name,
        created_date=wiki_post.created_date,
        topic_id=wiki_post.topic_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.passwordhash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = utils.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        fl_admin=False,  # ou True, conforme sua regra
        passwordhash=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

# ------------------- utilidades simples -------------------
@app.get("/")
def root():
    return {"msg": "Tea Hub API online"}
