"""
schemas.py

Pydantic models for Profile Management APIs.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


Role = Literal["job_seeker", "employer"]


class JobSeekerProfileCreate(BaseModel):
	full_name: str = Field(min_length=1, max_length=200)
	email: EmailStr
	phone: Optional[str] = Field(default=None, max_length=40)
	skills: Optional[str] = Field(default=None, max_length=5000)
	experience_years: Optional[int] = Field(default=None, ge=0, le=80)
	education: Optional[str] = Field(default=None, max_length=5000)


class JobSeekerProfileUpdate(BaseModel):
	full_name: Optional[str] = Field(default=None, max_length=200)
	email: Optional[EmailStr] = None
	phone: Optional[str] = Field(default=None, max_length=40)
	skills: Optional[str] = Field(default=None, max_length=5000)
	experience_years: Optional[int] = Field(default=None, ge=0, le=80)
	education: Optional[str] = Field(default=None, max_length=5000)


class JobSeekerProfilePublic(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	user_id: int
	full_name: str
	email: EmailStr
	phone: Optional[str] = None
	skills: Optional[str] = None
	experience_years: Optional[int] = None
	education: Optional[str] = None
	resume_url: Optional[str] = None
	created_at: datetime
	updated_at: datetime


class EmployerProfileCreate(BaseModel):
	company_name: str = Field(min_length=1, max_length=200)
	company_description: Optional[str] = Field(default=None, max_length=10000)
	website: Optional[str] = Field(default=None, max_length=320)
	location: Optional[str] = Field(default=None, max_length=200)
	contact_email: Optional[EmailStr] = None


class EmployerProfileUpdate(BaseModel):
	company_name: Optional[str] = Field(default=None, max_length=200)
	company_description: Optional[str] = Field(default=None, max_length=10000)
	website: Optional[str] = Field(default=None, max_length=320)
	location: Optional[str] = Field(default=None, max_length=200)
	contact_email: Optional[EmailStr] = None


class EmployerProfilePublic(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	user_id: int
	company_name: str
	company_description: Optional[str] = None
	website: Optional[str] = None
	location: Optional[str] = None
	contact_email: Optional[EmailStr] = None
	created_at: datetime
	updated_at: datetime


class ResumeUploadResponse(BaseModel):
	resume_url: str


