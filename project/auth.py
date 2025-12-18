"""
auth.py

Security utilities:
- bcrypt password hashing (Passlib)
- JWT creation/verification
- FastAPI dependencies for protected routes
- Role-based access checks

JWT is stored in an HTTP-only cookie for the UI routes.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Optional

import bcrypt
from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Support both package imports (`project.*`) and script-style imports when running
# `python main.py` from inside the `project` folder.
try:  # Package-style imports
    from project.database import get_db
    from project.models import User
except ImportError:  # Script-style imports
    from database import get_db
    from models import User


# -------------------------
# Password hashing (bcrypt)
# -------------------------
def _prehash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA-256 to avoid bcrypt's 72-byte limit.
    This ensures passwords of any length work correctly.
    Returns bytes (not hex string) for bcrypt compatibility.
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt. Pre-hashes with SHA-256 to handle
    passwords longer than 72 bytes (bcrypt's limit).
    Returns a bcrypt hash string.
    """
    prehashed = _prehash_password(password)
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prehashed, salt)
    # Return as string (bcrypt hashes are base64 encoded)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash. Pre-hashes the plain password
    with SHA-256 to match the hashing process.
    """
    prehashed = _prehash_password(plain_password)
    # Convert hash string back to bytes
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(prehashed, hashed_bytes)


# -------------------------
# JWT settings
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Cookie settings (Security Considerations)
COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def create_access_token(*, subject: str, role: str) -> str:
    """
    Creates a signed JWT with an expiry.
    subject: usually user email or user id (we use email for readability).
    role: used for RBAC checks.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Validates signature + expiry.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


def set_auth_cookie(response, token: str) -> None:
    """
    Stores JWT in an HTTP-only cookie. This is safer than localStorage against XSS.
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def clear_auth_cookie(response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")


# -------------------------
# Dependencies
# -------------------------
async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    # FastAPI >=0.115: default must be set outside of Annotated
    token_cookie: Annotated[Optional[str], Cookie(alias=COOKIE_NAME)] = None,
) -> User:
    """
    Reads JWT from either:
    - HTTP-only cookie (UI)
    - Authorization: Bearer <token> header (API clients)
    """
    token = token_cookie
    if not token:
        # Fallback to Authorization header
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")
    return user


Role = Literal["job_seeker", "employer"]


async def get_current_user_optional(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    # FastAPI >=0.115: default must be set outside of Annotated
    token_cookie: Annotated[Optional[str], Cookie(alias=COOKIE_NAME)] = None,
) -> Optional[User]:
    """
    UI-friendly dependency: returns None instead of raising 401/403.
    This still uses dependency injection, but lets UI routes redirect cleanly.
    """
    try:
        return await get_current_user(request=request, db=db, token_cookie=token_cookie)
    except HTTPException:
        return None


def require_role(*allowed: Role):
    """
    Dependency factory enforcing role-based access control.
    """

    async def _checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return user

    return _checker


