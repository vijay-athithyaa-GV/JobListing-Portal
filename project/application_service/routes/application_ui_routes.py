"""
application_service/routes/application_ui_routes.py

Employer UI route for reviewing applications.
Uses existing dashboard layout/styles (no new CSS).
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
    candidates = [Path("templates"), Path("project") / "templates"]
    for p in candidates:
        if p.is_dir():
            return str(p)
    return "templates"


templates = Jinja2Templates(directory=_get_templates_dir())

router = APIRouter()


@router.get("/applications/review", response_class=HTMLResponse)
async def review_application_page(
    request: Request,
    user: Annotated[User, Depends(require_role("employer"))],
    id: Optional[int] = Query(default=None),
):
    return templates.TemplateResponse(
        "review_application.html",
        {"request": request, "email": user.email, "role": user.role, "application_id": id},
    )


