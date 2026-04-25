"""Point d'entree du backend FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.app.api.v1.router import api_router
from server.app.core.config import get_settings
from server.app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise la base et les donnees de demo au demarrage."""
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Retourne l'etat global de l'API."""
    return {"status": "ok"}
