from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class PostStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    content: str = Column(Text, nullable=False)
    scheduled_at: datetime = Column(DateTime(timezone=True), nullable=False)
    status: PostStatus = Column(Enum(PostStatus), default=PostStatus.SCHEDULED, nullable=False)
    tweet_id: str | None = Column(String(64), nullable=True)
    error_message: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AppSetting(Base):
    """Key-value store for app settings (e.g. twikit cookies)."""
    __tablename__ = "app_settings"

    key: str = Column(String(128), primary_key=True)
    value: str = Column(Text, nullable=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_setting(key: str) -> str | None:
    async with async_session() as session:
        row = await session.get(AppSetting, key)
        return row.value if row else None


async def set_setting(key: str, value: str) -> None:
    async with async_session() as session:
        row = await session.get(AppSetting, key)
        if row:
            row.value = value
        else:
            session.add(AppSetting(key=key, value=value))
        await session.commit()
