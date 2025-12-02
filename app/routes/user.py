from fastapi import APIRouter, HTTPException, status
from app.database import db_dependency
from app.schemas.user import *
from app.services.auth import get_password_hash, verify_token
from app.models.user import *

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/register")
def register(user: UserSchema, db: db_dependency):
    hashed_pwd = get_password_hash(user.password)

    new_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        fl_admin=False,
        password_hash=hashed_pwd,
    )

    if db.query(User).filter(User.email == new_user.email).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email já registrado"
        )

    if db.query(User).filter(User.username == new_user.username).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuário já existe"
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}


def getReqUserByHeader(authorization: str, db: db_dependency):
    req_user = None
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Formato do token inválido")
        elif not len(authorization.split("Bearer ")) == 2:
            raise HTTPException(401, "É necessário um token válido para continuar")
        req_user = verify_token(db, authorization.split("Bearer ")[1])

    return req_user
