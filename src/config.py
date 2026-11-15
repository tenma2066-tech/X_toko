from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# X account credentials (for twikit — no API key needed)
X_USERNAME: str = os.getenv("X_USERNAME", "")
X_EMAIL: str = os.getenv("X_EMAIL", "")
X_PASSWORD: str = os.getenv("X_PASSWORD", "")

# Database — Render sets DATABASE_URL as postgres://, convert for async SQLAlchemy
_raw_db_url: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'x_toko.db'}")
if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_db_url.startswith("postgresql://"):
    _raw_db_url = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
DATABASE_URL: str = _raw_db_url

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
TZ: str = os.getenv("TZ", "Asia/Tokyo")
