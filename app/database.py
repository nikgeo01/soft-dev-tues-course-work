from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, event, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


class TimestampMixin:
    """Reusable created/updated timestamps (UTC-aware columns)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: object) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Enforce referential integrity on SQLite (off by default).
event.listen(engine.sync_engine, "connect", _set_sqlite_pragma)
