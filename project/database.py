"""
database.py

Async SQLAlchemy engine/session setup for PostgreSQL.
"""

import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def _get_database_url() -> str:
    """
    Get the database URL from the environment, with a sensible local default.

    The URL should look like:
    postgresql+asyncpg://user:password@host:5432/dbname
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback for local development so the app can start without extra config.
        # Adjust user/password/host/dbname here if your local Postgres is different.
        url = "postgresql+asyncpg://postgres:Vijay%402005@localhost:5432/job_portal"
    return url


DATABASE_URL = _get_database_url()

# echo can be toggled for debugging SQL queries
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides an AsyncSession per request.
    """
    async with AsyncSessionLocal() as session:
        yield session


