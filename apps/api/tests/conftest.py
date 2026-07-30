# ruff: noqa: E402

import os
from collections.abc import Generator
from pathlib import Path

import pytest

TEST_DATABASE_PATH = Path(__file__).parent / ".test-app.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"

from apps.api.main import engine, run_migrations


@pytest.fixture(autouse=True)
def isolated_database() -> Generator[None, None, None]:
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)
    run_migrations()
    yield
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)
