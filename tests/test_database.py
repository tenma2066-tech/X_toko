from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import Base, ScheduledPost, PostStatus


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_post(db_session: AsyncSession):
    post = ScheduledPost(
        content="Test tweet",
        scheduled_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    assert post.id is not None
    assert post.content == "Test tweet"
    assert post.status == PostStatus.SCHEDULED


@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession):
    post = ScheduledPost(
        content="Another tweet",
        scheduled_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
    )
    db_session.add(post)
    await db_session.commit()

    post.status = PostStatus.POSTED
    post.tweet_id = "123456789"
    await db_session.commit()
    await db_session.refresh(post)

    assert post.status == PostStatus.POSTED
    assert post.tweet_id == "123456789"


@pytest.mark.asyncio
async def test_query_scheduled(db_session: AsyncSession):
    for i in range(3):
        db_session.add(ScheduledPost(
            content=f"Tweet {i}",
            scheduled_at=datetime(2025, 6, 1, 12, i, tzinfo=timezone.utc),
            status=PostStatus.SCHEDULED if i < 2 else PostStatus.POSTED,
        ))
    await db_session.commit()

    result = await db_session.execute(
        select(ScheduledPost).where(ScheduledPost.status == PostStatus.SCHEDULED)
    )
    scheduled = result.scalars().all()
    assert len(scheduled) == 2
