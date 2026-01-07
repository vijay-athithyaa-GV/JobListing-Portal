"""
application_service/schemas.py

Pydantic schemas for job applications.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    jobId: int = Field(gt=0)


class ApplicationListItem(BaseModel):
    applicationId: int
    jobId: int
    jobTitle: str
    companyName: str
    status: Literal["pending", "accepted", "rejected"]
    appliedAt: datetime


class ApplicationSummary(BaseModel):
    total: int
    pending: int
    accepted: int
    rejected: int


class ApplicationsMeResponse(BaseModel):
    summary: ApplicationSummary
    applications: list[ApplicationListItem]


class ApplicationStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


