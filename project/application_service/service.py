"""
application_service/service.py

Service-layer abstraction for application operations.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EmployerProfile, JobApplication, JobListing, JobSeekerProfile, User


def _expose_status(db_value: str) -> str:
    return (db_value or "").lower()


class ApplicationService:
    @staticmethod
    async def apply(*, db: AsyncSession, job_id: int, job_seeker_id: int) -> JobApplication:
        # Ensure job exists and is ACTIVE
        job_res = await db.execute(select(JobListing).where(JobListing.job_id == job_id))
        job = job_res.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        if (job.status or "").upper() != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not active.")

        app = JobApplication(job_id=job_id, job_seeker_id=job_seeker_id, status="PENDING")
        db.add(app)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already applied to this job.")

        await db.refresh(app)
        return app

    @staticmethod
    async def list_my_applications(*, db: AsyncSession, job_seeker_id: int):
        # Join for job title + company name
        stmt = (
            select(
                JobApplication,
                JobListing.job_title,
                EmployerProfile.company_name,
            )
            .select_from(JobApplication)
            .join(JobListing, JobListing.job_id == JobApplication.job_id)
            .join(EmployerProfile, EmployerProfile.user_id == JobListing.employer_id, isouter=True)
            .where(JobApplication.job_seeker_id == job_seeker_id)
            .order_by(JobApplication.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.all())

    @staticmethod
    async def list_employer_recent(*, db: AsyncSession, employer_id: int, limit: int = 5):
        stmt = (
            select(
                JobApplication,
                JobListing.job_title,
                JobSeekerProfile.full_name,
                User.email,
            )
            .select_from(JobApplication)
            .join(JobListing, JobListing.job_id == JobApplication.job_id)
            .join(User, User.id == JobApplication.job_seeker_id)
            .join(JobSeekerProfile, JobSeekerProfile.user_id == JobApplication.job_seeker_id, isouter=True)
            .where(JobListing.employer_id == employer_id)
            .order_by(JobApplication.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.all())

    @staticmethod
    async def summarize_employer_applications(*, db: AsyncSession, employer_id: int) -> dict:
        base = (
            select(JobApplication.status, func.count())
            .select_from(JobApplication)
            .join(JobListing, JobListing.job_id == JobApplication.job_id)
            .where(JobListing.employer_id == employer_id)
            .group_by(JobApplication.status)
        )
        rows = (await db.execute(base)).all()
        counts = { (status or "").upper(): int(cnt) for status, cnt in rows }
        total = sum(counts.values())
        pending = counts.get("PENDING", 0)
        return {"total": total, "pending": pending}

    @staticmethod
    async def employer_job_counts(*, db: AsyncSession, employer_id: int) -> dict[int, int]:
        stmt = (
            select(JobApplication.job_id, func.count())
            .select_from(JobApplication)
            .join(JobListing, JobListing.job_id == JobApplication.job_id)
            .where(JobListing.employer_id == employer_id)
            .group_by(JobApplication.job_id)
        )
        rows = (await db.execute(stmt)).all()
        return {int(job_id): int(cnt) for job_id, cnt in rows}

    @staticmethod
    async def employer_get_application_detail(*, db: AsyncSession, employer_id: int, application_id: int) -> dict:
        stmt = (
            select(
                JobApplication,
                JobListing.job_title,
                JobListing.employer_id,
                User.email,
                JobSeekerProfile.full_name,
                JobSeekerProfile.skills,
                JobSeekerProfile.phone,
                JobSeekerProfile.resume_url,
            )
            .select_from(JobApplication)
            .join(JobListing, JobListing.job_id == JobApplication.job_id)
            .join(User, User.id == JobApplication.job_seeker_id)
            .join(JobSeekerProfile, JobSeekerProfile.user_id == JobApplication.job_seeker_id, isouter=True)
            .where(JobApplication.application_id == application_id)
        )
        row = (await db.execute(stmt)).one_or_none()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

        app, job_title, job_employer_id, email, full_name, skills, phone, resume_url = row
        if int(job_employer_id) != int(employer_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")

        candidate_name = full_name or (email or "")
        return {
            "applicationId": app.application_id,
            "jobId": app.job_id,
            "jobTitle": job_title,
            "status": ApplicationService.expose_status(app.status),
            "appliedAt": app.created_at,
            "candidate": {
                "name": candidate_name,
                "email": email or "",
                "phone": phone,
                "skills": skills,
                "resumeUrl": resume_url,
            },
        }

    @staticmethod
    async def employer_update_application_status(
        *, db: AsyncSession, employer_id: int, application_id: int, status_value: str
    ) -> dict:
        # Ensure ownership and fetch existing
        detail = await ApplicationService.employer_get_application_detail(
            db=db, employer_id=employer_id, application_id=application_id
        )

        new_status = status_value.strip().upper()
        if new_status == "ACCEPTED":
            db_status = "ACCEPTED"
        elif new_status == "REJECTED":
            db_status = "REJECTED"
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status.")

        res = await db.execute(select(JobApplication).where(JobApplication.application_id == application_id))
        app = res.scalar_one_or_none()
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
        app.status = db_status
        await db.commit()
        await db.refresh(app)

        detail["status"] = ApplicationService.expose_status(app.status)
        return detail

    @staticmethod
    async def summarize_my_applications(*, db: AsyncSession, job_seeker_id: int) -> dict:
        total = (await db.execute(select(func.count()).select_from(JobApplication).where(JobApplication.job_seeker_id == job_seeker_id))).scalar_one()
        pending = (
            (await db.execute(
                select(func.count()).select_from(JobApplication).where(
                    JobApplication.job_seeker_id == job_seeker_id,
                    JobApplication.status == "PENDING",
                )
            )).scalar_one()
        )
        accepted = (
            (await db.execute(
                select(func.count()).select_from(JobApplication).where(
                    JobApplication.job_seeker_id == job_seeker_id,
                    JobApplication.status == "ACCEPTED",
                )
            )).scalar_one()
        )
        rejected = (
            (await db.execute(
                select(func.count()).select_from(JobApplication).where(
                    JobApplication.job_seeker_id == job_seeker_id,
                    JobApplication.status == "REJECTED",
                )
            )).scalar_one()
        )
        return {
            "total": int(total),
            "pending": int(pending),
            "accepted": int(accepted),
            "rejected": int(rejected),
        }

    @staticmethod
    def expose_status(db_value: str) -> str:
        return _expose_status(db_value)


