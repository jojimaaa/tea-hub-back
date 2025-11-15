from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import data_routes, auth_routes, wiki_routes
from .database import engine
from . import models

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

models.Base.metadata.create_all(bind=engine)

try:
    app.include_router(data_routes.router, prefix="/data", tags=["dados"])
    app.include_router(auth_routes.router)
    app.include_router(wiki_routes.router)
except Exception as e:
    print(f"[main] Aviso: router de dados não incluído: {e}")

# ------------------- utilidades simples -------------------
@app.get("/")
def root():
    return {"msg": "Tea Hub API online"}
