from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def create_database_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        sqlite_path = database_url.split("///", 1)[1] if "///" in database_url else ""
        if sqlite_path and sqlite_path != ":memory:":
            Path(sqlite_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    engine_kwargs: dict[str, object] = {"future": True, "pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **engine_kwargs)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
