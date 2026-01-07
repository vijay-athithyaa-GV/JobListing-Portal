from contextlib import asynccontextmanager
import os
import logging
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional

load_dotenv(find_dotenv(usecwd=True))

try: 
    from database import engine, get_db
    from models import Base, Job
    from routes.auth_routes import router as auth_router
    from profile_service.routes.profile_routes import router as profile_router
    from profile_service.database import engine as profile_engine
    from profile_service.models import Base as ProfileBase
    from job_service.database import engine as job_engine
    from job_service.models import Base as JobServiceBase
    from job_service.routes.job_api_routes import router as job_api_router
    from job_service.routes.job_ui_routes import router as job_ui_router
    from application_service.database import engine as application_engine
    from application_service.models import Base as ApplicationBase
    from application_service.routes.application_routes import router as application_router
    from application_service.routes.application_ui_routes import router as application_ui_router
except ImportError:
    from project.database import engine, get_db
    from project.models import Base, Job
    from project.routes.auth_routes import router as auth_router
    from project.profile_service.routes.profile_routes import router as profile_router
    from project.profile_service.database import engine as profile_engine
    from project.profile_service.models import Base as ProfileBase
    from project.job_service.database import engine as job_engine
    from project.job_service.models import Base as JobServiceBase
    from project.job_service.routes.job_api_routes import router as job_api_router
    from project.job_service.routes.job_ui_routes import router as job_ui_router
    from project.application_service.database import engine as application_engine
    from project.application_service.models import Base as ApplicationBase
    from project.application_service.routes.application_routes import router as application_router
    from project.application_service.routes.application_ui_routes import router as application_ui_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with profile_engine.begin() as conn:
        await conn.run_sync(ProfileBase.metadata.create_all)
    async with job_engine.begin() as conn:
        await conn.run_sync(JobServiceBase.metadata.create_all)
    async with application_engine.begin() as conn:
        await conn.run_sync(ApplicationBase.metadata.create_all)
    yield

app = FastAPI(title="Job Listing Portal", lifespan=lifespan)

logger = logging.getLogger("job_portal")

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request, exc: ResponseValidationError):
    """
    Make ResponseValidationErrors easy to debug in development by logging
    the exact route/method that triggered them.
    """
    # Use print so this shows up even if logging config is not wired.
    print(
        f"ResponseValidationError on {request.method} {request.url.path}: {exc.errors()}",
        flush=True,
    )
    logger.exception(
        "ResponseValidationError on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Response validation failed on the server.",
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

PROFILE_SERVICE_DIR = os.path.join(BASE_DIR, "profile_service")
PROFILE_UPLOADS_DIR = os.path.join(PROFILE_SERVICE_DIR, "uploads")
if os.path.isdir(PROFILE_UPLOADS_DIR):
    app.mount("/uploads", StaticFiles(directory=PROFILE_UPLOADS_DIR), name="uploads")

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(job_ui_router)
app.include_router(job_api_router)
app.include_router(application_router)
app.include_router(application_ui_router)

@app.get("/jobs/search", tags=["Job Search"])
async def search_jobs(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_salary: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Job)
    if keyword:
        stmt = stmt.where(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.description.ilike(f"%{keyword}%")
            )
        )
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if min_salary:
        stmt = stmt.where(Job.salary >= min_salary)

    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)