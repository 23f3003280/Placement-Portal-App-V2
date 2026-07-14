import os
from celery import Celery
from celery.schedules import crontab

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
reminder_hour = int(os.environ.get("REMINDER_HOUR", "24"))
reminder_minute = int(os.environ.get("REMINDER_MINUTE", "0"))

celery = Celery(
    "ppa_tasks",
    broker=redis_url,
    backend=redis_url,
)

# load celery config from environment if present
celery.conf.beat_schedule = {
    # daily reminders at a configurable time (default 08:00)
    "daily-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=reminder_hour, minute=reminder_minute),
    },
    # monthly report roughly every 30 days
    "monthly-report": {
        "task": "tasks.generate_monthly_report",
        "schedule": 60 * 60 * 24 * 30,
    },
}
