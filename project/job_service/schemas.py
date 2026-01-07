"""
job_service/schemas.py

Pydantic schemas for the Job Listing microservice.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


JobType = Literal["Full-time", "Part-time", "Internship", "Contract"]


class JobCreate(BaseModel):
    jobTitle: str = Field(min_length=1, max_length=255)
    jobDescription: str = Field(min_length=1)
    qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    jobType: JobType
    location: str = Field(min_length=1, max_length=200)
    salaryRange: Optional[str] = Field(default=None, max_length=120)


class JobUpdate(BaseModel):
    jobTitle: Optional[str] = Field(default=None, min_length=1, max_length=255)
    jobDescription: Optional[str] = Field(default=None, min_length=1)
    qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    jobType: Optional[JobType] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    salaryRange: Optional[str] = Field(default=None, max_length=120)
    status: Optional[Literal["draft", "active", "closed", "DRAFT", "ACTIVE", "CLOSED"]] = None


class JobEmployerListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: int
    jobTitle: str
    status: str
    createdAt: datetime
    applicationsCount: int = 0


class JobPublicListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: int
    jobTitle: str
    companyName: str
    location: str
    jobType: str
    salaryRange: Optional[str] = None
    createdAt: datetime


class JobDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: int
    jobTitle: str
    companyName: Optional[str] = None
    location: str
    jobType: str
    salaryRange: Optional[str] = None
    status: str
    jobDescription: str
    qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


