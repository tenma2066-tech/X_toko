"""X posting client using twikit (no API key, no fees)."""

from __future__ import annotations

import json
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from twikit import Client

from src.config import X_USERNAME, X_EMAIL, X_PASSWORD
from src.database import get_setting, set_setting

logger = logging.getLogger(__name__)

_client: Client | None = None
_COOKIES_KEY = "twikit_cookies"


@dataclass
class TweetResult:
    success: bool
    tweet_id: str | None = None
    error: str | None = None


async def _get_client() -> Client:
    global _client
    if _client is not None:
        return _client

    client = Client("ja")

    saved = await get_setting(_COOKIES_KEY)
    if saved:
        try:
            tmp = Path(tempfile.mktemp(suffix=".json"))
            tmp.write_text(saved, encoding="utf-8")
            client.load_cookies(str(tmp))
            tmp.unlink(missing_ok=True)
            _client = client
            logger.info("Loaded saved cookies")
            return _client
        except Exception as exc:
            logger.warning("Saved cookies invalid, re-login needed: %s", exc)

    if not all([X_USERNAME, X_PASSWORD]):
        raise RuntimeError(
            "X credentials not configured. Set X_USERNAME, X_EMAIL, X_PASSWORD in environment variables."
        )

    logger.info("Logging in to X as @%s ...", X_USERNAME)
    await client.login(auth_info_1=X_USERNAME, auth_info_2=X_EMAIL, password=X_PASSWORD)
    await _save_cookies(client)
    _client = client
    logger.info("Login successful")
    return _client


async def _save_cookies(client: Client) -> None:
    tmp = Path(tempfile.mktemp(suffix=".json"))
    client.save_cookies(str(tmp))
    cookies_json = tmp.read_text(encoding="utf-8")
    tmp.unlink(missing_ok=True)
    await set_setting(_COOKIES_KEY, cookies_json)


async def post_tweet(text: str) -> TweetResult:
    try:
        client = await _get_client()
    except Exception as exc:
        return TweetResult(success=False, error=f"Login failed: {exc}")

    try:
        tweet = await client.create_tweet(text=text)
        await _save_cookies(client)
        return TweetResult(success=True, tweet_id=str(tweet.id))
    except Exception as exc:
        logger.error("Tweet failed: %s", exc)
        _reset_client()
        return TweetResult(success=False, error=str(exc))


def _reset_client() -> None:
    global _client
    _client = None


async def check_login() -> tuple[bool, str]:
    try:
        client = await _get_client()
        user = await client.user()
        return True, f"@{user.screen_name} としてログイン中"
    except Exception as exc:
        _reset_client()
        return False, str(exc)
