"""Scheduler that checks for due posts and publishes them."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from src.database import ScheduledPost, PostStatus, async_session
from src.x_client import post_tweet

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _process_due_posts() -> None:
    now = datetime.now(timezone.utc)

    async with async_session() as session:
        stmt = (
            select(ScheduledPost)
            .where(ScheduledPost.status == PostStatus.SCHEDULED)
            .where(ScheduledPost.scheduled_at <= now)
            .order_by(ScheduledPost.scheduled_at)
        )
        result = await session.execute(stmt)
        posts = result.scalars().all()

    for post in posts:
        logger.info("Posting scheduled tweet id=%d", post.id)
        tweet_result = await post_tweet(post.content)

        async with async_session() as session:
            db_post = await session.get(ScheduledPost, post.id)
            if db_post is None:
                continue
            if tweet_result.success:
                db_post.status = PostStatus.POSTED
                db_post.tweet_id = tweet_result.tweet_id
                logger.info("Tweet posted: id=%d, tweet_id=%s", post.id, tweet_result.tweet_id)
            else:
                db_post.status = PostStatus.FAILED
                db_post.error_message = tweet_result.error
                logger.error("Tweet failed: id=%d, error=%s", post.id, tweet_result.error)
            await session.commit()

        await asyncio.sleep(1)


def start_scheduler() -> None:
    scheduler.add_job(_process_due_posts, "interval", seconds=30, id="process_due_posts", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started — checking every 30 seconds")


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
