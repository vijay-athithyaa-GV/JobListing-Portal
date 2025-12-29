"""
security.py

JWT verification and role-based dependencies for the Profile service.
This mirrors the Auth service approach and expects the same SECRET_KEY
and ALGORITHM configuration. Tokens are read from an HTTP-only cookie
named 'access_token' or from the Authorization header (Bearer).
"""

import os
from datetime import datetime, timezone
from typing import Annotated, Optional, Literal

from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User


Role = Literal["job_seeker", "employer"]

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
COOKIE_NAME = "access_token"


def decode_access_token(token: str) -> dict:
	try:
		return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token.",
		)


class CurrentUser:
	def __init__(self, id: int, email: str, role: Role):
		self.id = id
		self.email = email
		self.role = role


async def get_current_user(
	request: Request,
	db: Annotated[AsyncSession, Depends(get_db)],
	token_cookie: Annotated[Optional[str], Cookie(alias=COOKIE_NAME)] = None,
) -> CurrentUser:
	"""
	Read JWT from cookie or Authorization header. Resolve user id by email.
	"""
	token = token_cookie
	if not token:
		auth = request.headers.get("Authorization")
		if auth and auth.lower().startswith("bearer "):
			token = auth.split(" ", 1)[1].strip()

	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

	payload = decode_access_token(token)
	email = payload.get("sub")
	role = payload.get("role")
	if not email or not role:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

	result = await db.execute(select(User).where(User.email == str(email).lower()))
	user = result.scalar_one_or_none()
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

	return CurrentUser(id=user.id, email=user.email, role=role)  # type: ignore[arg-type]


def require_role(*allowed: Role):
	async def _checker(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
		if user.role not in allowed:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You do not have permission to access this resource.",
			)
		return user

	return _checker


async def get_current_user_optional(
	request: Request,
	db: Annotated[AsyncSession, Depends(get_db)],
	token_cookie: Annotated[Optional[str], Cookie(alias=COOKIE_NAME)] = None,
) -> Optional[CurrentUser]:
	"""
	UI-friendly dependency: returns None instead of raising 401/403,
	so routes can redirect to /login cleanly when unauthenticated.
	"""
	try:
		return await get_current_user(request=request, db=db, token_cookie=token_cookie)
	except HTTPException:
		return None


