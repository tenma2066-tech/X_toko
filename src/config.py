from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

X_API_KEY: str = os.getenv("X_API_KEY", "")
X_API_SECRET: str = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN: str = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET: str = os.getenv("X_ACCESS_TOKEN_SECRET", "")
X_BEARER_TOKEN: str = os.getenv("X_BEARER_TOKEN", "")

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'x_toko.db'}")
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
TZ: str = os.getenv("TZ", "Asia/Tokyo")
