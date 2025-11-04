from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services import auth_service
from app.database import db_dependency
from app.schemas import *
from app.services import auth_service
from . import models

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(
    user: UserCreate, 
    db: db_dependency
):
    hashed_pwd = auth_service.get_password_hash(user.password)
    
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

@router.post("/login", response_model=Token)
def login(
    db: db_dependency, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )
    
    if not user or not auth_service.verify_password(form_data.password, user.passwordhash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
        
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}