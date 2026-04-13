from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from .core.config import get_settings, reset_settings_cache
from .migrations import run_migrations
from . import models  # noqa: F401


def _ensure_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    raw_path = database_url.replace("sqlite:///", "", 1)
    if raw_path == ":memory:":
        return
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_engine():
    settings = get_settings()
    _ensure_sqlite_directory(settings.database_url)
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, echo=False, connect_args=connect_args)


def reset_engine_cache() -> None:
    get_engine.cache_clear()
    reset_settings_cache()


def init_db() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    run_migrations(engine)


def get_session():
    with Session(get_engine()) as session:
        yield session
