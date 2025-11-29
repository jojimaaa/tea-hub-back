from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from app.database import db_dependency
from app.schemas.auth import *
from app.services.auth import *
from app.models.user import *

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenSchema)
def login(
    db: db_dependency, 
    form_data: LoginSchema
):
    user = (
        db.query(User)
        .filter(User.email == form_data.email)
        .first()
    )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
        
    access_token = create_access_token(user.name, user.username)
    refresh_token = create_access_token(user.name, user.username, timedelta(hours=4))

    print(user.username)
    print(user.name)
    print(access_token)
    print(refresh_token)
    response = {"username": user.username, "name": user.name,"access_token": access_token, "refresh_token": refresh_token,"token_type": "Bearer"}

    return response

@router.post("/login-form", response_model=TokenSchema)
def login(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
        
    access_token = create_access_token(user.name, user.username)
    refresh_token = create_access_token(user.name, user.username, timedelta(hours=4))
    response = {"username": user.username, "name": user.name,"access_token": access_token, "refresh_token": refresh_token,"token_type": "Bearer"}

    return response

@router.post("/refresh")
async def refresh_token(db: db_dependency, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Authorization header obrigatório")

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Formato do token inválido")
    elif not len(authorization.split("Bearer "))==2:
        raise HTTPException(401, "É necessário um token válido para continuar")

    token = authorization.split("Bearer ")[1]
    
    user = verify_token(db, token) 

    access_token = create_access_token(user.name, user.username)
    
    return{
        "access_token": access_token,
        "token_type": "Bearer"
    }