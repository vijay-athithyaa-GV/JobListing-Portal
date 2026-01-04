"""
routes/profile_routes.py

Contains:
- JSON APIs under /profiles/*
- UI pages (Jinja2 templates) for viewing and editing profiles
"""

from pathlib import Path
import os
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import EmployerProfile, JobSeekerProfile
from ..schemas import (
	EmployerProfileCreate,
	EmployerProfilePublic,
	EmployerProfileUpdate,
	JobSeekerProfileCreate,
	JobSeekerProfilePublic,
	JobSeekerProfileUpdate,
	ResumeUploadResponse,
)
from ..security import CurrentUser, get_current_user, require_role
from ..security import get_current_user_optional


BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

# Base URL for the Auth service login redirection
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://127.0.0.1:8000")

# -------------------------
# API endpoints - Job Seeker
# -------------------------
@router.get("/profiles/jobseeker/me")
async def get_my_job_seeker_profile(
	user: Annotated[CurrentUser, Depends(require_role("job_seeker"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	result = await db.execute(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user.id))
	profile = result.scalar_one_or_none()
	if not profile:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
	# Return plain dict to avoid response validation issues if ORM serialization isn't enabled.
	return JobSeekerProfilePublic.model_validate(profile).model_dump()


@router.post("/profiles/jobseeker", status_code=status.HTTP_201_CREATED)
async def create_job_seeker_profile(
	payload: JobSeekerProfileCreate,
	user: Annotated[CurrentUser, Depends(require_role("job_seeker"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	existing = await db.execute(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user.id))
	if existing.scalar_one_or_none():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists.")

	profile = JobSeekerProfile(
		user_id=user.id,
		full_name=payload.full_name,
		email=str(payload.email).lower(),
		phone=payload.phone,
		skills=payload.skills,
		experience_years=payload.experience_years,
		education=payload.education,
	)
	db.add(profile)
	try:
		await db.commit()
	except IntegrityError:
		await db.rollback()
		raise
	await db.refresh(profile)
	return JobSeekerProfilePublic.model_validate(profile).model_dump()


@router.put("/profiles/jobseeker")
async def update_job_seeker_profile(
	payload: JobSeekerProfileUpdate,
	user: Annotated[CurrentUser, Depends(require_role("job_seeker"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	result = await db.execute(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user.id))
	profile = result.scalar_one_or_none()
	if not profile:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

	# Apply partial updates
	if payload.full_name is not None:
		profile.full_name = payload.full_name
	if payload.email is not None:
		profile.email = str(payload.email).lower()
	if payload.phone is not None:
		profile.phone = payload.phone
	if payload.skills is not None:
		profile.skills = payload.skills
	if payload.experience_years is not None:
		profile.experience_years = payload.experience_years
	if payload.education is not None:
		profile.education = payload.education

	await db.commit()
	await db.refresh(profile)
	return JobSeekerProfilePublic.model_validate(profile).model_dump()


@router.post("/profiles/jobseeker/resume")
async def upload_resume(
	file: UploadFile,
	user: Annotated[CurrentUser, Depends(require_role("job_seeker"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	result = await db.execute(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user.id))
	profile = result.scalar_one_or_none()
	if not profile:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

	# Validate file type and size (PDF only, <= 2MB)
	content_type = (file.content_type or "").lower()
	if content_type != "application/pdf":
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")
	contents = await file.read()
	max_size_bytes = 2 * 1024 * 1024
	if len(contents) > max_size_bytes:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 2MB limit.")

	# Save file
	uploads_dir = BASE_DIR / "uploads" / "resumes"
	uploads_dir.mkdir(parents=True, exist_ok=True)
	filename = f"user_{user.id}_resume.pdf"
	dest = uploads_dir / filename
	dest.write_bytes(contents)

	public_url = f"/uploads/resumes/{filename}"
	profile.resume_url = public_url

	await db.commit()
	return {"resume_url": public_url}


# -------------------------
# API endpoints - Employer
# -------------------------
@router.get("/profiles/employer/me")
async def get_my_employer_profile(
	user: Annotated[CurrentUser, Depends(require_role("employer"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	result = await db.execute(select(EmployerProfile).where(EmployerProfile.user_id == user.id))
	profile = result.scalar_one_or_none()
	if not profile:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
	return EmployerProfilePublic.model_validate(profile).model_dump()


@router.post("/profiles/employer", status_code=status.HTTP_201_CREATED)
async def create_employer_profile(
	payload: EmployerProfileCreate,
	user: Annotated[CurrentUser, Depends(require_role("employer"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	existing = await db.execute(select(EmployerProfile).where(EmployerProfile.user_id == user.id))
	if existing.scalar_one_or_none():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists.")

	profile = EmployerProfile(
		user_id=user.id,
		company_name=payload.company_name,
		company_description=payload.company_description,
		website=payload.website,
		location=payload.location,
		contact_email=str(payload.contact_email).lower() if payload.contact_email else None,
	)
	db.add(profile)
	try:
		await db.commit()
	except IntegrityError:
		await db.rollback()
		raise
	await db.refresh(profile)
	return EmployerProfilePublic.model_validate(profile).model_dump()


@router.put("/profiles/employer")
async def update_employer_profile(
	payload: EmployerProfileUpdate,
	user: Annotated[CurrentUser, Depends(require_role("employer"))],
	db: Annotated[AsyncSession, Depends(get_db)],
):
	result = await db.execute(select(EmployerProfile).where(EmployerProfile.user_id == user.id))
	profile = result.scalar_one_or_none()
	if not profile:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

	if payload.company_name is not None:
		profile.company_name = payload.company_name
	if payload.company_description is not None:
		profile.company_description = payload.company_description
	if payload.website is not None:
		profile.website = payload.website
	if payload.location is not None:
		profile.location = payload.location
	if payload.contact_email is not None:
		profile.contact_email = str(payload.contact_email).lower() if payload.contact_email else None

	await db.commit()
	await db.refresh(profile)
	return EmployerProfilePublic.model_validate(profile).model_dump()


# -------------------------
# UI routes (protected)
# -------------------------
@router.get("/profile/jobseeker", response_class=HTMLResponse)
async def jobseeker_profile_page(
	request: Request,
	user: Annotated[CurrentUser | None, Depends(get_current_user_optional)],
):
	if not user:
		return RedirectResponse(url=f"{AUTH_BASE_URL}/login", status_code=status.HTTP_302_FOUND)
	# Redirect employer to their page
	if user.role == "employer":
		return templates.TemplateResponse("role_redirect.html", {"request": request, "target": "/profile/employer"})
	return templates.TemplateResponse("jobseeker_profile.html", {"request": request, "role": user.role})


@router.get("/profile/employer", response_class=HTMLResponse)
async def employer_profile_page(
	request: Request,
	user: Annotated[CurrentUser | None, Depends(get_current_user_optional)],
):
	if not user:
		return RedirectResponse(url=f"{AUTH_BASE_URL}/login", status_code=status.HTTP_302_FOUND)
	# Redirect job seeker to their page
	if user.role == "job_seeker":
		return templates.TemplateResponse("role_redirect.html", {"request": request, "target": "/profile/jobseeker"})
	return templates.TemplateResponse("employer_profile.html", {"request": request, "role": user.role})


@router.get("/profile/jobseeker/edit", response_class=HTMLResponse)
async def edit_jobseeker_profile_page(
	request: Request,
	user: Annotated[CurrentUser, Depends(require_role("job_seeker"))],
):
	return templates.TemplateResponse("edit_jobseeker_profile.html", {"request": request})


@router.get("/profile/employer/edit", response_class=HTMLResponse)
async def edit_employer_profile_page(
	request: Request,
	user: Annotated[CurrentUser, Depends(require_role("employer"))],
):
	return templates.TemplateResponse("edit_employer_profile.html", {"request": request})


