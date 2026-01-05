"""
main.py

FastAPI application entrypoint for the Job Listing Portal.

Run:
  uvicorn project.main:app --reload
"""

from contextlib import asynccontextmanager
import os

from fastapi import Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

# Swagger security
security = HTTPBearer()

# Support both package imports and script execution
try:
    from project.database import engine
    from project.routes.auth_routes import router as auth_router
    from project.routes.jobs import router as jobs_router
    from project.models import Base

except ImportError:
    from database import engine
    from routes.auth_routes import router as auth_router
    from routes.jobs import router as jobs_router
    from models import Base




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create tables at startup.
    (In production, use Alembic migrations)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Job Listing Portal",
    lifespan=lifespan
)


# 🔐 Swagger JWT Authorize configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Job Listing Portal",
        version="1.0.0",
        description="Job Listing APIs with JWT Authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [
        {"BearerAuth": []}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# ✅ REGISTER custom Swagger
app.openapi = custom_openapi


# Static assets (CSS / JS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)



# Routes
app.include_router(auth_router)
app.include_router(jobs_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=302)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


from project.auth import get_current_user_optional

@app.get("/job-listings", response_class=HTMLResponse)
async def job_listings(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "job_listings.html",
        {"request": request}
    )


@app.get("/job-form", response_class=HTMLResponse)
async def job_form(request: Request):
    return templates.TemplateResponse(
        "job_form.html",
        {"request": request}
    )

@app.get("/job-view", response_class=HTMLResponse)
async def job_view(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "job_view.html",
        {"request": request},
    )
