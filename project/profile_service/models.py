"""
models.py

SQLAlchemy ORM models for Profile Management.
Includes:
- JobSeekerProfile
- EmployerProfile

Additionally includes a minimal User model mapping (read-only) to resolve
user_id from email when decoding JWT claims. Assumes both services share
the same PostgreSQL database.
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	pass


class User(Base):
	"""
	Lightweight mapping of the existing users table from the Auth service.
	Used to resolve user_id from email embedded in JWT.
	"""
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
	# other fields are not needed for profile service context


class JobSeekerProfile(Base):
	__tablename__ = "job_seeker_profiles"
	__table_args__ = (UniqueConstraint("user_id", name="uq_job_seeker_profiles_user_id"),)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

	full_name: Mapped[str] = mapped_column(String(200), nullable=False)
	email: Mapped[str] = mapped_column(String(320), nullable=False)
	phone: Mapped[str] = mapped_column(String(40), nullable=True)
	skills: Mapped[str] = mapped_column(Text, nullable=True)  # comma-separated or JSON (simple text here)
	experience_years: Mapped[int] = mapped_column(Integer, nullable=True)
	education: Mapped[str] = mapped_column(Text, nullable=True)
	resume_url: Mapped[str] = mapped_column(String(1024), nullable=True)

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class EmployerProfile(Base):
	__tablename__ = "employer_profiles"
	__table_args__ = (UniqueConstraint("user_id", name="uq_employer_profiles_user_id"),)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

	company_name: Mapped[str] = mapped_column(String(200), nullable=False)
	company_description: Mapped[str] = mapped_column(Text, nullable=True)
	website: Mapped[str] = mapped_column(String(320), nullable=True)
	location: Mapped[str] = mapped_column(String(200), nullable=True)
	contact_email: Mapped[str] = mapped_column(String(320), nullable=True)

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


