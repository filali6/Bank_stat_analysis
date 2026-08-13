from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for every ORM model in the app."""


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Creates every table that doesn't exist yet. Safe to call on
    every startup — it never drops or alters existing tables."""
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)