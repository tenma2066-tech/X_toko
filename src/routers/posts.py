from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from src.database import ScheduledPost, PostStatus, async_session
from src.models import PostCreate, PostUpdate, PostResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# --- Web UI routes ---

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    async with async_session() as session:
        stmt = select(ScheduledPost).order_by(ScheduledPost.scheduled_at.desc())
        result = await session.execute(stmt)
        posts = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@router.get("/new", response_class=HTMLResponse)
async def new_post_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@router.get("/edit/{post_id}", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int):
    async with async_session() as session:
        post = await session.get(ScheduledPost, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})


# --- API routes ---

@router.get("/api/posts", response_model=list[PostResponse])
async def list_posts(status: str | None = None):
    async with async_session() as session:
        stmt = select(ScheduledPost).order_by(ScheduledPost.scheduled_at.desc())
        if status:
            stmt = stmt.where(ScheduledPost.status == status)
        result = await session.execute(stmt)
        return result.scalars().all()


@router.post("/api/posts", response_model=PostResponse, status_code=201)
async def create_post(body: PostCreate):
    post = ScheduledPost(content=body.content, scheduled_at=body.scheduled_at)
    async with async_session() as session:
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post


@router.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, body: PostUpdate):
    async with async_session() as session:
        post = await session.get(ScheduledPost, post_id)
        if not post:
            raise HTTPException(404, "Post not found")
        if post.status != PostStatus.SCHEDULED:
            raise HTTPException(400, "投稿済み・失敗・キャンセル済みの投稿は編集できません")
        if body.content is not None:
            post.content = body.content
        if body.scheduled_at is not None:
            post.scheduled_at = body.scheduled_at
        await session.commit()
        await session.refresh(post)
        return post


@router.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(post_id: int):
    async with async_session() as session:
        post = await session.get(ScheduledPost, post_id)
        if not post:
            raise HTTPException(404, "Post not found")
        if post.status == PostStatus.SCHEDULED:
            post.status = PostStatus.CANCELLED
            await session.commit()
        else:
            await session.delete(post)
            await session.commit()


@router.post("/api/posts/{post_id}/retry", response_model=PostResponse)
async def retry_post(post_id: int):
    async with async_session() as session:
        post = await session.get(ScheduledPost, post_id)
        if not post:
            raise HTTPException(404, "Post not found")
        if post.status != PostStatus.FAILED:
            raise HTTPException(400, "失敗した投稿のみリトライできます")
        post.status = PostStatus.SCHEDULED
        post.error_message = None
        post.scheduled_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(post)
        return post
