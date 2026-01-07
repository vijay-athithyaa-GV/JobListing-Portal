"""
job_service/database.py

Async SQLAlchemy engine/session setup for the Job Listing microservice.
Uses the same PostgreSQL database by default to keep local development simple.
"""

import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(find_dotenv(usecwd=True))


def _get_database_url() -> str:
    url = os.getenv("JOB_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        url = "postgresql+asyncpg://postgres:bavaguru12@localhost:5432/job_listing_db"
    return url


DATABASE_URL = _get_database_url()

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


