"""
jobs.py

Routes for job listings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from project.database import get_db
from project.models import Job, User
from project.schemas import JobCreate, JobUpdate, JobPublic
from project.auth import get_current_user


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobPublic, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create job listings",
        )

    new_job = Job(
        title=job.title,
        description=job.description,
        qualifications=job.qualifications,
        responsibilities=job.responsibilities,
        location=job.location,
        salary_range=job.salary_range,
        employer_id=current_user.id,
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    return new_job


@router.get("/", response_model=list[JobPublic])
async def get_my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can view their jobs",
        )

    result = await db.execute(
        select(Job).where(Job.employer_id == current_user.id)
    )
    jobs = result.scalars().all()
    return jobs


@router.put("/{job_id}", response_model=JobPublic)
async def update_job(
    job_id: int,
    job: JobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    existing_job = result.scalars().first()

    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if current_user.role != "employer" or existing_job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job",
        )

    existing_job.title = job.title
    existing_job.description = job.description
    existing_job.qualifications = job.qualifications
    existing_job.responsibilities = job.responsibilities
    existing_job.location = job.location
    existing_job.salary_range = job.salary_range

    await db.commit()
    await db.refresh(existing_job)

    return existing_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if current_user.role != "employer" or job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job",
        )

    await db.delete(job)
    await db.commit()

    return
