# Mazingira Plan

Mazingira Plan is a Kenya-focused circular economy platform that helps people turn waste items into practical outcomes. Users upload an item, receive AI-powered reuse/repurpose/disposal guidance, and can connect with local repair experts for hands-on support.

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

## screenshots
- Landing Page
  <img width="1893" height="939" alt="Screenshot 2025-11-27 190502" src="https://github.com/user-attachments/assets/9bfbf955-a5f7-4382-8697-2c574b85a79d" />

-Dashboards
<img width="1908" height="930" alt="Screenshot 2025-11-27 190728" src="https://github.com/user-attachments/assets/e300b47f-18ae-4d43-8583-4b5b233f7ff2" />


<img width="1919" height="960" alt="Screenshot 2025-11-27 190914" src="https://github.com/user-attachments/assets/38f65e36-54a8-4c08-998c-dfd83b6fb07a" />


<img width="1916" height="958" alt="Screenshot 2025-11-27 191127" src="https://github.com/user-attachments/assets/d2fb9c5f-ba55-446a-8915-bd0fb67ef973" />


<img width="1891" height="962" alt="Screenshot 2025-11-27 191423" src="https://github.com/user-attachments/assets/0a8ff1ab-dd5f-439a-ab0d-afe5dbb01e5b" />


<img width="1901" height="952" alt="Screenshot 2025-11-27 191708" src="https://github.com/user-attachments/assets/902aa828-a898-4fdf-b478-831237b06417" />



<img width="1890" height="865" alt="Screenshot 2025-11-27 191530" src="https://github.com/user-attachments/assets/cbf7b294-abf6-4374-854d-8a0251609d43" />


<img width="1899" height="941" alt="Screenshot 2025-11-27 191931" src="https://github.com/user-attachments/assets/64f84550-9dea-4b22-b035-971701829d73" />



<img width="1891" height="962" alt="Screenshot 2025-11-27 191423" src="https://github.com/user-attachments/assets/ca19eb9c-49e2-49f2-9efb-30eeaea7b1e6" />


<img width="1898" height="955" alt="Screenshot 2025-11-24 214022" src="https://github.com/user-attachments/assets/ed26490b-8e03-4d47-9303-62707f5bf9f5" />


<img width="1901" height="945" alt="Screenshot 2025-11-24 213208" src="https://github.com/user-attachments/assets/e706849c-5546-4cce-a93f-1b19befcd0cc" />


<img width="1901" height="958" alt="Screenshot 2025-11-24 132738" src="https://github.com/user-attachments/assets/5beba448-3e77-4026-bb77-c5b5e2374f90" />
