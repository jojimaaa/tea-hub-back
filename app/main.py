from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, data, wiki, forum, user
from .database import engine, Base

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.56.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

try:
    app.include_router(data.router)
    app.include_router(auth.router)
    app.include_router(wiki.router)
    app.include_router(forum.router)
    app.include_router(user.router)
except Exception as e:
    print(f"[main] Aviso: router de dados não incluído: {e}")

# ------------------- utilidades simples -------------------
@app.get("/")
def root():
    return {"msg": "Tea Hub API online"}
