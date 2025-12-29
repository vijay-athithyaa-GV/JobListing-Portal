## Profile Management Service (FastAPI + Jinja2)

Independent microservice for Job Seeker and Employer profiles.
Follows the same frontend pattern as the Auth service: server-rendered Jinja2, vanilla JS, and dark theme CSS.

### Run (dev)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r .\profile_service\requirements.txt
uvicorn profile_service.main:app --reload --port 8001
```

### Configuration

Environment variables (examples):

```powershell
$env:PROFILE_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/job_portal"
$env:SECRET_KEY="change-me-in-prod"  # MUST match Auth service
```

This service expects to share the same PostgreSQL database as the Auth service so it can resolve `user_id` via the `users` table using the JWT `sub` (email).

### API

Base URL: `http://127.0.0.1:8001`

Auth: JWT via cookie `access_token` or `Authorization: Bearer <token>` header.

#### Job Seeker

- GET `/profiles/jobseeker/me` → 200
```json
{
  "id": 1,
  "user_id": 42,
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "555-1234",
  "skills": "Python, SQL, FastAPI",
  "experience_years": 4,
  "education": "BSc Computer Science",
  "resume_url": "/uploads/resumes/user_42_resume.pdf",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

- POST `/profiles/jobseeker` (create)
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "555-1234",
  "skills": "Python, SQL, FastAPI",
  "experience_years": 4,
  "education": "BSc Computer Science"
}
```
→ 201 returns JobSeekerProfilePublic

- PUT `/profiles/jobseeker` (update) → 200 returns JobSeekerProfilePublic

- POST `/profiles/jobseeker/resume` (multipart/form-data with `file`) → 200
```json
{ "resume_url": "/uploads/resumes/user_42_resume.pdf" }
```

Errors:
- 400: Invalid file type/size, profile exists
- 401: Not authenticated
- 403: Wrong role
- 404: Profile not found

#### Employer

- GET `/profiles/employer/me` → 200 returns EmployerProfilePublic
- POST `/profiles/employer` → 201 returns EmployerProfilePublic
- PUT `/profiles/employer` → 200 returns EmployerProfilePublic

### UI Routes

- GET `/profile/jobseeker` → Job Seeker profile page
- GET `/profile/employer` → Employer profile page
- GET `/profile/jobseeker/edit` → Edit Job Seeker profile form
- GET `/profile/employer/edit` → Edit Employer profile form

All UI routes are protected and rely on the JWT cookie (or Authorization header).

### Notes

- File uploads are stored locally under `profile_service/uploads/resumes/` and served at `/uploads/resumes/*`.
- In production, replace with S3/Cloud storage and a signed URL mechanism.
- This service is intentionally framework-free on the frontend (no React/Vue). Jinja2 + vanilla JS only.


