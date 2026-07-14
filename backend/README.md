Backend Placement Portal (Flask + Celery)

Quick start (local):

1. Create and activate a virtualenv, install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start Redis (required for Celery):

```bash
# if you have redis installed locally
redis-server &
```

3. Seed database and create admin:

```bash
python seed.py
```

4. Start Flask app:

```bash
export FLASK_APP=app.py
python app.py
```

5. Start Celery worker and (optionally) beat:

```bash
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```

Default admin credentials: `admin@institute.edu` / `adminpass` (override with `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables)

## Added functionality

- Monthly placement reports as HTML via `/api/admin/report/monthly`
- Student application export as CSV via `/api/student/export-applications`
- Daily reminder summary via `/api/admin/notifications/reminders`
- Lightweight cache for admin summary and drive listing endpoints