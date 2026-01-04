# JobListing Portal (Backend)

This is a backend API built using **FastAPI** for managing job listings.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- JWT Authentication

## Setup Instructions

1. Clone the repository

```bash
git clone <repo-url>
cd JobListing-Portal

pip install -r requirements.txt

## Run the server
python -m uvicorn project.main:app --reload

## open in browser
http://127.0.0.1:8000/docs

## Authentication
- Use `/auth/login` to generate JWT token
- Authorize via Swagger UI
- Use token for protected routes
```
