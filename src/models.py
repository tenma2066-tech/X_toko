from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)
    scheduled_at: datetime

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("投稿内容は空にできません")
        return v


class PostUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=280)
    scheduled_at: datetime | None = None


class PostResponse(BaseModel):
    id: int
    content: str
    scheduled_at: datetime
    status: str
    tweet_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
