from fastapi import FastAPI

from .routers import data_routes, auth_routes, wiki_routes
from .database import engine
from . import models

app = FastAPI()

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
