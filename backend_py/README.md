# backend_py (Django + DRF)

Secure Django REST backend replacing Node.js API.

## Setup

1. Create and configure `.env` (see `.env.example`).
2. Install Python 3.11+ and pip.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run migrations: `python manage.py migrate`.
5. Create superuser: `python manage.py createsuperuser`.
6. Start server: `python manage.py runserver`.

## Docker

Use `docker-compose up --build` to run Postgres + app.
