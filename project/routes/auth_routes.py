"""
routes/auth_routes.py

Contains:
- JSON APIs under /auth/*
- UI pages and UI routes (Jinja2 templates)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# Support both package imports (`project.*`) and script-style imports when running
# `python main.py` from inside the `project` folder.
try:  # Package-style imports
    from project.auth import (
        clear_auth_cookie,
        create_access_token,
        get_current_user,
        get_current_user_optional,
        hash_password,
        set_auth_cookie,
        verify_password,
    )
    from project.database import get_db
    from project.models import User
    from project.schemas import TokenResponse, UserCreate, UserLogin, UserPublic
    templates = Jinja2Templates(directory="project/templates")
except ImportError:  # Script-style imports
    from auth import (
        clear_auth_cookie,
        create_access_token,
        get_current_user,
        get_current_user_optional,
        hash_password,
        set_auth_cookie,
        verify_password,
    )
    from database import get_db
    from models import User
    from schemas import TokenResponse, UserCreate, UserLogin, UserPublic
    templates = Jinja2Templates(directory="templates")

router = APIRouter()


# -------------------------
# API endpoints
# -------------------------
@router.post("/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Create a new user.
    """
    user = User(
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    await db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    payload: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
):
    """
    Verify credentials and issue a JWT.

    The JWT is also set in an HTTP-only cookie for the UI.
    """
    result = await db.execute(select(User).where(User.email == str(payload.email).lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")

    token = create_access_token(subject=user.email, role=user.role)
    set_auth_cookie(response, token)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserPublic)
async def me(user: Annotated[User, Depends(get_current_user)]):
    """
    Protected endpoint returning the current user.
    """
    return user


@router.post("/auth/logout")
async def api_logout(response: Response):
    """
    Stateless JWT logout (server can't revoke without a blacklist).
    For UI usage we clear the auth cookie, effectively logging out the browser session.
    """
    clear_auth_cookie(response)
    return {"detail": "Logged out."}


# -------------------------
# UI routes
# -------------------------
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    role_label = "Job Seeker" if user.role == "job_seeker" else "Employer"
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "email": user.email,
            "role": user.role,
            "role_label": role_label,
        },
    )


@router.get("/logout")
async def logout():
    """
    UI logout: clear cookie then redirect to login.
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    clear_auth_cookie(response)
    return response


