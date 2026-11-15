from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models import PostCreate, PostUpdate, PostResponse


class TestPostCreate:
    def test_valid(self):
        p = PostCreate(content="Hello", scheduled_at=datetime.now(timezone.utc))
        assert p.content == "Hello"

    def test_strips_whitespace(self):
        p = PostCreate(content="  Hello  ", scheduled_at=datetime.now(timezone.utc))
        assert p.content == "Hello"

    def test_empty_content_rejected(self):
        with pytest.raises(ValidationError):
            PostCreate(content="", scheduled_at=datetime.now(timezone.utc))

    def test_whitespace_only_rejected(self):
        with pytest.raises(ValidationError):
            PostCreate(content="   ", scheduled_at=datetime.now(timezone.utc))

    def test_max_length(self):
        with pytest.raises(ValidationError):
            PostCreate(content="a" * 281, scheduled_at=datetime.now(timezone.utc))

    def test_280_chars_ok(self):
        p = PostCreate(content="a" * 280, scheduled_at=datetime.now(timezone.utc))
        assert len(p.content) == 280


class TestPostUpdate:
    def test_partial_update(self):
        p = PostUpdate(content="Updated")
        assert p.content == "Updated"
        assert p.scheduled_at is None

    def test_empty_update(self):
        p = PostUpdate()
        assert p.content is None
        assert p.scheduled_at is None
