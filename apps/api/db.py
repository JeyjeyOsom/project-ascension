import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent


def _load_env_file() -> None:
    for env_path in [
        BASE_DIR.parents[1] / ".env",
        BASE_DIR / ".env",
    ]:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env_file()

DEFAULT_DATABASE_PATH = BASE_DIR / "app.db"
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")
    if postgres_user and postgres_password and postgres_db:
        DATABASE_URL = f"postgresql+psycopg://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}"
    else:
        DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
