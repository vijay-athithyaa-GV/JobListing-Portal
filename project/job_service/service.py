"""
job_service/service.py

Service-layer abstraction for Job Listing operations.
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EmployerProfile, JobListing


def _normalize_status(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return "ACTIVE"
    upper = v.upper()
    if upper in {"DRAFT", "ACTIVE", "CLOSED"}:
        return upper
    # Accept UI-friendly lowercase strings
    if v.lower() in {"draft", "active", "closed"}:
        return v.upper()
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status.")


def _expose_status(db_value: str) -> str:
    # UI badge logic expects lowercase keys
    return (db_value or "").lower()


class JobService:
    @staticmethod
    async def create_job(*, db: AsyncSession, employer_id: int, payload) -> JobListing:
        job = JobListing(
            employer_id=employer_id,
            job_title=payload.jobTitle,
            job_description=payload.jobDescription,
            qualifications=payload.qualifications,
            responsibilities=payload.responsibilities,
            job_type=payload.jobType,
            location=payload.location,
            salary_range=payload.salaryRange,
            status="ACTIVE",
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def list_employer_jobs(*, db: AsyncSession, employer_id: int) -> list[JobListing]:
        stmt: Select = select(JobListing).where(JobListing.employer_id == employer_id).order_by(JobListing.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_public_jobs(
        *, db: AsyncSession, status_filter: Optional[str] = None
    ) -> list[tuple[JobListing, Optional[str]]]:
        stmt = (
            select(JobListing, EmployerProfile.company_name)
            .select_from(JobListing)
            .join(EmployerProfile, EmployerProfile.user_id == JobListing.employer_id, isouter=True)
            .order_by(JobListing.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(JobListing.status == _normalize_status(status_filter))
        result = await db.execute(stmt)
        return list(result.all())

    @staticmethod
    async def get_job(*, db: AsyncSession, job_id: int) -> tuple[JobListing, Optional[str]]:
        stmt = (
            select(JobListing, EmployerProfile.company_name)
            .select_from(JobListing)
            .join(EmployerProfile, EmployerProfile.user_id == JobListing.employer_id, isouter=True)
            .where(JobListing.job_id == job_id)
        )
        result = await db.execute(stmt)
        row = result.one_or_none()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        return row[0], row[1]

    @staticmethod
    async def require_owner(*, db: AsyncSession, job_id: int, employer_id: int) -> JobListing:
        result = await db.execute(select(JobListing).where(JobListing.job_id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        if job.employer_id != employer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")
        return job

    @staticmethod
    async def update_job(*, db: AsyncSession, job_id: int, employer_id: int, payload) -> JobListing:
        job = await JobService.require_owner(db=db, job_id=job_id, employer_id=employer_id)

        data = {}
        if payload.jobTitle is not None:
            data["job_title"] = payload.jobTitle
        if payload.jobDescription is not None:
            data["job_description"] = payload.jobDescription
        if payload.qualifications is not None:
            data["qualifications"] = payload.qualifications
        if payload.responsibilities is not None:
            data["responsibilities"] = payload.responsibilities
        if payload.jobType is not None:
            data["job_type"] = payload.jobType
        if payload.location is not None:
            data["location"] = payload.location
        if payload.salaryRange is not None:
            data["salary_range"] = payload.salaryRange
        if payload.status is not None:
            data["status"] = _normalize_status(payload.status)

        if data:
            await db.execute(update(JobListing).where(JobListing.job_id == job_id).values(**data))
            await db.commit()
            await db.refresh(job)
        return job

    @staticmethod
    async def delete_job(*, db: AsyncSession, job_id: int, employer_id: int) -> None:
        await JobService.require_owner(db=db, job_id=job_id, employer_id=employer_id)
        await db.execute(delete(JobListing).where(JobListing.job_id == job_id))
        await db.commit()

    @staticmethod
    async def count_employer_jobs(*, db: AsyncSession, employer_id: int) -> tuple[int, int]:
        total_stmt = select(func.count()).select_from(JobListing).where(JobListing.employer_id == employer_id)
        active_stmt = select(func.count()).select_from(JobListing).where(
            JobListing.employer_id == employer_id, JobListing.status == "ACTIVE"
        )
        total = (await db.execute(total_stmt)).scalar_one()
        active = (await db.execute(active_stmt)).scalar_one()
        return int(total), int(active)

    @staticmethod
    def expose_status(db_value: str) -> str:
        return _expose_status(db_value)


