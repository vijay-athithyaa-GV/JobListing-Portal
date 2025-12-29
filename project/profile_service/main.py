"""
main.py

FastAPI application entrypoint for the Profile Management service.
This service provides Job Seeker and Employer profile management with
server-rendered UI (Jinja2) and JSON APIs. It mirrors the look & feel
of the authentication module (dark theme, card UI).
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Load .env early so database/security pick up env vars before import side-effects
load_dotenv()

# Local imports
from .database import engine
from .models import Base
from .routes.profile_routes import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""
	Create tables at startup. In production, prefer Alembic migrations.
	"""
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield


app = FastAPI(title="Job Listing Portal - Profile Service", lifespan=lifespan)

# Static assets and uploads
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads" / "resumes"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# Expose uploads as public URLs; in production, serve via CDN/object storage
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "uploads")), name="uploads")

# Routes (API + UI)
app.include_router(profile_router)


@app.get("/")
async def root():
	# Send users to their role-specific profile; page will redirect based on role.
	return RedirectResponse(url="/profile/jobseeker", status_code=302)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(
		"profile_service.main:app",
		host="127.0.0.1",
		port=int(os.getenv("PORT", "8001")),
		reload=True,
	)


