"""
schemas.py

Pydantic models used by the authentication APIs.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


Role = Literal["job_seeker", "employer"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------------------------
# Job Schemas
# -------------------------

class JobBase(BaseModel):
    title: str
    description: str
    qualifications: str | None = None
    responsibilities: str | None = None
    location: str
    salary_range: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    pass


class JobPublic(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employer_id: int

