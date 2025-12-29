"""
main.py

FastAPI application entrypoint for the Authentication module.

Run:
  uvicorn project.main:app --reload
"""

from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Load .env early so DB config is available on import
load_dotenv()

# Support both package imports (when run via `uvicorn project.main:app`)
# and direct script execution (`python main.py` from inside the `project` folder).
try:  # Package-style imports
    from project.database import engine
    from project.models import Base
    from project.routes.auth_routes import router as auth_router
except ImportError:  # Script-style imports
    from database import engine
    from models import Base
    from routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create tables at startup (simple approach for this module).
    In production you would typically use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Job Listing Portal - Auth Module", lifespan=lifespan)

# Static assets for CSS/JS (path resolved relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routes (API + UI)
app.include_router(auth_router)


@app.get("/")
async def root():
    # Send users to the protected dashboard; it will redirect to /login if not authenticated.
    return RedirectResponse(url="/dashboard", status_code=302)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
