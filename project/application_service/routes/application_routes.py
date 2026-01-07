"""
application_service/routes/application_routes.py

REST API endpoints for applying to jobs and listing job seeker applications.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from project.auth import require_role
    from project.models import User
except ImportError:
    from auth import require_role
    from models import User

from ..database import get_db
from ..schemas import ApplicationCreate, ApplicationsMeResponse, ApplicationStatusUpdate
from ..service import ApplicationService


router = APIRouter(prefix="", tags=["Applications"])


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    payload: ApplicationCreate,
    user: Annotated[User, Depends(require_role("job_seeker"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    app = await ApplicationService.apply(db=db, job_id=payload.jobId, job_seeker_id=user.id)
    return {"applicationId": app.application_id, "status": ApplicationService.expose_status(app.status)}


@router.get("/applications/me", response_model=ApplicationsMeResponse)
async def my_applications(
    user: Annotated[User, Depends(require_role("job_seeker"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await ApplicationService.list_my_applications(db=db, job_seeker_id=user.id)
    summary = await ApplicationService.summarize_my_applications(db=db, job_seeker_id=user.id)

    applications = []
    for app, job_title, company_name in rows:
        applications.append(
            {
                "applicationId": app.application_id,
                "jobId": app.job_id,
                "jobTitle": job_title,
                "companyName": company_name or "",
                "status": ApplicationService.expose_status(app.status),
                "appliedAt": app.created_at,
            }
        )

    return {"summary": summary, "applications": applications}


@router.get("/applications/employer/recent")
async def employer_recent_applications(
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=5, ge=1, le=50),
):
    rows = await ApplicationService.list_employer_recent(db=db, employer_id=user.id, limit=limit)
    items = []
    for app, job_title, full_name, email in rows:
        candidate = full_name or (email or "")
        items.append(
            {
                "applicationId": app.application_id,
                "jobId": app.job_id,
                "candidateName": candidate,
                "jobTitle": job_title,
                "status": ApplicationService.expose_status(app.status),
                "appliedAt": app.created_at,
            }
        )
    return items


@router.get("/applications/employer/summary")
async def employer_applications_summary(
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await ApplicationService.summarize_employer_applications(db=db, employer_id=user.id)


@router.get("/applications/employer/job-counts")
async def employer_job_application_counts(
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    counts = await ApplicationService.employer_job_counts(db=db, employer_id=user.id)
    # JSON-friendly keys
    return {str(k): v for k, v in counts.items()}


@router.get("/applications/employer/{application_id}")
async def employer_get_application(
    application_id: int,
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await ApplicationService.employer_get_application_detail(db=db, employer_id=user.id, application_id=application_id)


@router.put("/applications/employer/{application_id}")
async def employer_update_application(
    application_id: int,
    payload: ApplicationStatusUpdate,
    user: Annotated[User, Depends(require_role("employer"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await ApplicationService.employer_update_application_status(
        db=db, employer_id=user.id, application_id=application_id, status_value=payload.status
    )


