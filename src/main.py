"""X Scheduled Posting System — entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.database import init_db
from src.scheduler import start_scheduler, stop_scheduler
from src.routers.posts import router as posts_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="X 定期投稿システム", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(posts_router)
