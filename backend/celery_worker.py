import os
from celery import Celery

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "ppa_tasks",
    broker=redis_url,
    backend=redis_url,
)

# load celery config from environment if present
celery.conf.beat_schedule = {
    # daily reminders at 08:00
    "daily-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": 60 * 60 * 24,
    },
    # monthly report roughly every 30 days
    "monthly-report": {
        "task": "tasks.generate_monthly_report",
        "schedule": 60 * 60 * 24 * 30,
    },
}
