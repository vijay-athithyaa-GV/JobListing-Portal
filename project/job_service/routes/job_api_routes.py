"""
job_service/routes/job_api_routes.py

REST API endpoints for the Job Listing microservice.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# Support both package imports (`project.*`) and script-style imports.
try:
    from project.auth import get_current_user, require_role
    from project.models import User
except ImportError:
    from auth import get_current_user, require_role
    from models import User

from ..database import get_db
from ..schemas import JobCreate, JobDetail, JobEmployerListItem, JobPublicListItem, JobUpdate
from ..service import JobService


router = APIRouter(prefix="", tags=["Jobs"])


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    job = await JobService.create_job(db=db, employer_id=user.id, payload=payload)
    return {
        "jobId": job.job_id,
        "jobTitle": job.job_title,
        "status": JobService.expose_status(job.status),
        "createdAt": job.created_at,
        "updatedAt": job.updated_at,
    }


@router.get("/jobs")
async def list_jobs(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    employerId: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    """
    - Employer view: GET /jobs?employerId=<id> (restricted to that employer)
    - Public browse: GET /jobs?status=ACTIVE (authenticated user)
    """
    if employerId is not None:
        # Employer-only listing (owner)
        if user.role != "employer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")
        if user.id != employerId:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")
        jobs = await JobService.list_employer_jobs(db=db, employer_id=employerId)
        return [
            JobEmployerListItem(
                jobId=j.job_id,
                jobTitle=j.job_title,
                status=JobService.expose_status(j.status),
                createdAt=j.created_at,
                applicationsCount=0,
            ).model_dump()
            for j in jobs
        ]

    # Public list (job seekers) - filter by status
    rows = await JobService.list_public_jobs(db=db, status_filter=status)
    items: list[dict] = []
    for job, company_name in rows:
        items.append(
            JobPublicListItem(
                jobId=job.job_id,
                jobTitle=job.job_title,
                companyName=company_name or "",
                location=job.location,
                jobType=job.job_type,
                salaryRange=job.salary_range,
                createdAt=job.created_at,
            ).model_dump()
        )
    return items


@router.get("/jobs/{job_id}")
async def view_job(
    job_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    job, company_name = await JobService.get_job(db=db, job_id=job_id)
    return JobDetail(
        jobId=job.job_id,
        jobTitle=job.job_title,
        companyName=company_name or "",
        location=job.location,
        jobType=job.job_type,
        salaryRange=job.salary_range,
        status=JobService.expose_status(job.status),
        jobDescription=job.job_description,
        qualifications=job.qualifications,
        responsibilities=job.responsibilities,
        createdAt=job.created_at,
        updatedAt=job.updated_at,
    ).model_dump()


@router.put("/jobs/{job_id}")
async def edit_job(
    job_id: int,
    payload: JobUpdate,
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    job = await JobService.update_job(db=db, job_id=job_id, employer_id=user.id, payload=payload)
    return {
        "jobId": job.job_id,
        "jobTitle": job.job_title,
        "status": JobService.expose_status(job.status),
        "createdAt": job.created_at,
        "updatedAt": job.updated_at,
    }


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await JobService.delete_job(db=db, job_id=job_id, employer_id=user.id)
    return None


