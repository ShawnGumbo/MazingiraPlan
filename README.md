# Panolive

Panolive is a Kenya-focused circular economy platform that helps people turn waste items into practical outcomes. Users upload an item, receive AI-powered reuse/repurpose/disposal guidance, and can connect with local repair experts for hands-on support.

## What It Does

- Environmental users:
  - Register and sign in
  - Upload waste items (image + description)
  - Get structured AI suggestions
  - View personal item history
  - Request help from experts
- Repair experts:
  - Sign in and view connection requests
  - Accept or reject requests
  - Share eco tips
- Administrators:
  - Sign in through the regular auth page and get redirected to admin dashboard
  - Verify/unverify experts
  - Moderate requests and submissions
  - Manage suggestion knowledge base
  - Monitor live dashboard metrics

## Tech Stack

- Backend: Django, Django REST Framework, SimpleJWT, PostgreSQL
- Frontend: React + Vite, React Router, Axios
- Maps: Leaflet + OpenStreetMap
- AI: Google Gemini via google-genai

## Project Structure

- `panolive_backend/`: Django project settings and root routing
- `users/`: main backend app (models, APIs, serializers, tests, migrations)
- `frontend/`: React client app
- `docs/`: architecture and requirements traceability docs

## Quick Start

### 1. Backend setup

```bash
# from project root
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create your local env file from `.env.example` and fill in real values.

Run migrations and backend server:

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: http://127.0.0.1:5173
Backend API base URL: http://127.0.0.1:8000/api/

## Environment Variables

Use `.env.example` as the template.

Required variables include:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DJANGO_CORS_ALLOW_ALL`
- `GEMINI_API_KEY`

## Core API Endpoints

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/token/refresh/`
- `GET /api/experts/`
- `POST /api/submit-item/`
- `GET /api/my-items/`
- `GET/POST /api/job-requests/`
- `POST /api/job-requests/<id>/respond/`
- `GET/POST /api/eco-tips/`
- `GET /api/admin/dashboard-summary/`

## Quality Checks

Backend tests:

```bash
python manage.py test
```

Frontend lint + build:

```bash
cd frontend
npm run lint
npm run build
```

## Notes

- Do not commit real secrets; keep them in local `.env` files.
- `venv/`, `frontend/node_modules/`, and `frontend/dist/` are intentionally ignored.
