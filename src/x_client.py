"""X (Twitter) API v2 client — Free tier (write-only, 1,500 tweets/month)."""

from __future__ import annotations

import hashlib
import hmac
import base64
import time
import urllib.parse
import uuid
from dataclasses import dataclass

import httpx

from src.config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

TWEET_ENDPOINT = "https://api.twitter.com/2/tweets"


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def _build_oauth_header(method: str, url: str, body_params: dict | None = None) -> str:
    oauth_params = {
        "oauth_consumer_key": X_API_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": X_ACCESS_TOKEN,
        "oauth_version": "1.0",
    }

    all_params = {**oauth_params}
    if body_params:
        all_params.update(body_params)

    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in sorted(all_params.items())
    )
    base_string = f"{method.upper()}&{_percent_encode(url)}&{_percent_encode(sorted_params)}"
    signing_key = f"{_percent_encode(X_API_SECRET)}&{_percent_encode(X_ACCESS_TOKEN_SECRET)}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params["oauth_signature"] = signature
    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"' for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


@dataclass
class TweetResult:
    success: bool
    tweet_id: str | None = None
    error: str | None = None


async def post_tweet(text: str) -> TweetResult:
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        return TweetResult(success=False, error="X API credentials not configured. Check .env file.")

    auth_header = _build_oauth_header("POST", TWEET_ENDPOINT)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                TWEET_ENDPOINT,
                json={"text": text},
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            return TweetResult(success=False, error=f"Network error: {exc}")

    if resp.status_code == 201:
        data = resp.json()
        return TweetResult(success=True, tweet_id=data["data"]["id"])

    try:
        err_body = resp.json()
        detail = err_body.get("detail") or err_body.get("title") or str(err_body)
    except Exception:
        detail = resp.text
    return TweetResult(success=False, error=f"HTTP {resp.status_code}: {detail}")
