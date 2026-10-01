# Navratri QR-Based Prop Distribution System

Django 5 application for a **single organization / single event** Navratri distribution flow.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Environment variables

- `SECRET_KEY`
- `DATABASE_URL` (PostgreSQL in production)
- `FERNET_KEY` (for encrypted QR token storage)
- `QR_HASH_KEY` (HMAC key for token lookup)
- `ALLOWED_HOSTS`, `DEBUG`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`

## Main features

- Custom user roles: `ADMIN` and `STAFF`
- Participant registration with one secure QR token each
- Hash-based token lookup (`HMAC-SHA256`) + optional encrypted token persistence
- Centralized IST date utility (`apps/core/dates.py`)
- Event date singleton config
- Scanner + explicit claim APIs (`/scanner/api/scan/`, `/scanner/api/claim/`)
- Atomic duplicate prevention via DB unique constraint on claim
- QR regenerate audit log
- CSV reports with formula injection protection

## Production deployment (minimal)

1. PostgreSQL + `DATABASE_URL`
2. `DEBUG=False`, `ALLOWED_HOSTS` set
3. HTTPS via Nginx + Let's Encrypt
4. `gunicorn config.wsgi:application --workers 3 --threads 2`
5. `python manage.py collectstatic`
6. `python manage.py compilemessages`

## Backups

- Daily PostgreSQL backup with `pg_dump`
- Media directory backup (`media/`)
- Keep `SECRET_KEY` + `FERNET_KEY` safely backed up

## Operational usage

1. Admin configures event dates.
2. Admin registers participants and prints/distributes QR cards.
3. Staff scans QR, verifies participant, then clicks **GIVE PROP**.
4. Admin monitors stats and exports reports.
