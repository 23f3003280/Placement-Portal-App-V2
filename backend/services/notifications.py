import os
from datetime import datetime, timedelta
from typing import List

from models import Drive, User


def get_upcoming_deadlines(days_ahead: int = 2) -> list:
    cutoff = datetime.utcnow() + timedelta(days=days_ahead)
    return Drive.query.filter(Drive.application_deadline != None).filter(Drive.application_deadline <= cutoff).all()


def build_reminder_message(drive: Drive) -> str:
    return f"Reminder: the deadline for '{drive.title}' is approaching. Please review the drive details soon."


def send_daily_reminders() -> dict:
    students = User.query.filter_by(role='student').all()
    upcoming = get_upcoming_deadlines()
    message_count = 0
    for student in students:
        if not student.email:
            continue
        message_count += 1
    return {
        'checked_students': len(students),
        'upcoming_drives': len(upcoming),
        'message_count': message_count,
        'generated_at': datetime.utcnow().isoformat(),
    }
