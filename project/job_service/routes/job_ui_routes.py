"""
job_service/routes/job_ui_routes.py

UI routes for /jobs/post and /jobs/browse.
These pages reuse the existing dashboard layout and design system (no new styles).
"""

from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

try:
    from project.auth import require_role
    from project.models import User
except ImportError:
    from auth import require_role
    from models import User


def _get_templates_dir() -> str:
    """
    Support both:
    - running from repo root: ./templates
    - package-style layouts: ./project/templates
    """
    candidates = [Path("templates"), Path("project") / "templates"]
    for p in candidates:
        if p.is_dir():
            return str(p)
    return "templates"


templates = Jinja2Templates(directory=_get_templates_dir())


router = APIRouter()


@router.get("/jobs/post", response_class=HTMLResponse)
async def post_job_page(
    request: Request,
    user: Annotated[User, Depends(require_role("employer"))],
    id: Optional[int] = Query(default=None),
):
    # id is optional; if provided the frontend will load job details for editing.
    return templates.TemplateResponse(
        "post_job.html",
        {"request": request, "email": user.email, "role": user.role, "job_id": id},
    )


@router.get("/jobs/browse", response_class=HTMLResponse)
async def browse_jobs_page(
    request: Request,
    user: Annotated[User, Depends(require_role("job_seeker"))],
):
    return templates.TemplateResponse(
        "browse_jobs.html",
        {"request": request, "email": user.email, "role": user.role},
    )


