"""
job_service/models.py

SQLAlchemy ORM models for the Job Listing microservice.
Also includes lightweight mappings for related tables (users/employer_profiles) for read-only joins.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Lightweight mapping of the existing users table from the Auth service.
    Needed so SQLAlchemy can resolve ForeignKey("users.id") during create_all.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class JobListing(Base):
    __tablename__ = "job_listings"

    job_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    qualifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)

    job_type: Mapped[str] = mapped_column(String(32), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    salary_range: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Stored uppercase for reliable filtering, exposed as lowercase in API for UI compatibility
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class EmployerProfile(Base):
    """
    Lightweight mapping of employer_profiles (owned by profile_service) for companyName lookups.
    """

    __tablename__ = "employer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)


