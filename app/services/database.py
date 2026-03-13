"""
MongoDB connection using Motor (async driver) and helper utilities.
"""

from __future__ import annotations
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME: str = os.getenv("DB_NAME", "adaptive_engine")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[DB_NAME]


# Collection accessors --------------------------------------------------

def questions_col():
    return get_db()["questions"]


def sessions_col():
    return get_db()["sessions"]


# Lifecycle hooks -------------------------------------------------------

async def connect_db() -> None:
    """Called on application startup."""
    client = get_client()
    # Verify connection
    await client.admin.command("ping")
    # Create indexes
    await questions_col().create_index("question_id", unique=True)
    await questions_col().create_index("difficulty")
    await questions_col().create_index("topic")
    await sessions_col().create_index("session_id", unique=True)
    print(f"[DB] Connected to MongoDB at {MONGO_URI} / database '{DB_NAME}'")


async def close_db() -> None:
    """Called on application shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
        print("[DB] MongoDB connection closed.")
