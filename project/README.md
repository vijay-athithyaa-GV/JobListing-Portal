# Job Listing Portal 🧑‍💼💼

A full-stack Job Listing Portal built using **FastAPI**, **SQLAlchemy (Async)**, and **Vanilla JavaScript**.

Employers can:

- Register & Login
- Create, update, delete job listings
- View job previews
- Manage only their own jobs securely

---

## 🚀 Tech Stack

### Backend

- FastAPI
- Async SQLAlchemy
- SQLite / PostgreSQL
- JWT Authentication
- Jinja2 Templates

### Frontend

- HTML
- CSS
- Vanilla JavaScript (Fetch API)

---

## 🔐 Authentication

- JWT-based authentication
- Role-based access (`employer`)
- Protected routes using FastAPI dependencies

---

## 📌 Features

- Employer authentication (Login / Logout)
- Create job listings
- Update job listings
- Delete job listings
- View job preview
- Secure access (only employer can manage their jobs)

---

## ▶️ Run Locally

### 1️⃣ Create virtual environment

```bash
python -m venv .venv

## Activate
.venv\Scripts\activate

## install dependencis
pip install -r project/requirements.txt

## run server
uvicorn project.main:app --reload

App URLs
Login: http://127.0.0.1:8000/login
Dashboard: http://127.0.0.1:8000/dashboard
Job Listings: http://127.0.0.1:8000/job-listings
Create Job: http://127.0.0.1:8000/job-form
```
