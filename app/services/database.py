"""MongoDB connection using Motor's async driver."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

# Support both names so local .env files and Render configuration work.
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME", "adaptive_engine")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[DB_NAME]


def questions_col():
    return get_db()["questions"]


def sessions_col():
    return get_db()["sessions"]


async def connect_db() -> None:
    """Verify MongoDB connectivity and create useful indexes."""
    client = get_client()
    await client.admin.command("ping")
    await questions_col().create_index("question_id", unique=True)
    await questions_col().create_index("difficulty")
    await questions_col().create_index("topic")
    await sessions_col().create_index("session_id", unique=True)
    print(f"[DB] Connected to MongoDB / database '{DB_NAME}'")


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("[DB] MongoDB connection closed.")
