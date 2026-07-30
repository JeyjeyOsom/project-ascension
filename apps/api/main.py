from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.db import DATABASE_URL, engine, get_db
from apps.api.handlers.auth import router as auth_router
from apps.api.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


def _get_alembic_config() -> Config:
    config = Config(str(Path(__file__).resolve().parent / "alembic.ini"))
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parent / "alembic")
    )
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


def run_migrations() -> None:
    command.upgrade(_get_alembic_config(), "head")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "project-ascension-api",
        "version": "0.1.0",
    }


__all__ = ["DATABASE_URL", "Base", "app", "engine", "get_db", "run_migrations"]
