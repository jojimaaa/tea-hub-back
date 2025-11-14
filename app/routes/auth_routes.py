from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services import auth_service
from app.database import db_dependency
from app.schemas import *
from app.services.auth_service import *
from app import models

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(
    user: UserSchema, 
    db: db_dependency
):
    hashed_pwd = get_password_hash(user.password)
    
    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        fl_admin=False,
        password_hash=hashed_pwd
    )
    
    if (db.query(models.User).filter(models.User.email == new_user.email).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email já registrado"
        )
        
    if (db.query(models.User).filter(models.User.username == new_user.username).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário já existe"
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@router.post("/login", response_model=TokenSchema)
def login(
    db: db_dependency, 
    form_data: LoginSchema
):
    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
        
    access_token = create_access_token(user.email)
    refresh_token = create_access_token(user.email, timedelta(hours=3))
    return {"username": user.username, "name": user.name,"access_token": access_token, "refresh_token": refresh_token,"token_type": "Bearer"}

@router.post("/login-form", response_model=TokenSchema)
def login(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
        
    access_token = create_access_token(user.email)
    return {"username": user.username, "name": user.name,"access_token": access_token, "token_type": "Bearer"}

@router.get("/refresh-token")
def refresh_token(user: validation_dependency):
    access_token = create_access_token(user.email)
    
    return{
        "access_token": access_token,
        "token_type": "Bearer"
    }