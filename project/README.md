## Job Listing Portal — Authentication Module (FastAPI + UI)

This folder contains **ONLY** the User Authentication module (Registration, Login, JWT, RBAC) with a simple UI (Jinja2 + HTML/CSS/JS).

### Tech stack
- FastAPI + Jinja2 templates
- PostgreSQL
- SQLAlchemy (async) + asyncpg
- JWT auth (HTTP-only cookie)
- Passlib (bcrypt)

### Setup (Windows PowerShell)
Create and activate a virtualenv, then install deps:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\project\requirements.txt
```

### Configure environment
Set these environment variables (PowerShell examples):

```powershell
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/job_portal"
$env:SECRET_KEY="change-me-in-prod"
$env:ACCESS_TOKEN_EXPIRE_MINUTES="60"
$env:COOKIE_SECURE="false"
```

Notes:
- **DATABASE_URL** must point to a PostgreSQL database (created ahead of time).
- **COOKIE_SECURE** should be `true` in production (HTTPS).

### Run

```bash
uvicorn project.main:app --reload
```

Open:
- `/register`
- `/login`
- `/dashboard` (protected)


