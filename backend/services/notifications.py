import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from models import Drive, User


def get_upcoming_deadlines(days_ahead: int = 5) -> list:
    cutoff = datetime.utcnow() + timedelta(days=days_ahead)
    return Drive.query.filter(Drive.application_deadline != None).filter(Drive.application_deadline <= cutoff).all()


def build_reminder_message(upcoming_drives: list[Drive]) -> str:
    if not upcoming_drives:
        return 'Reminder: please review the latest placement drives and application deadlines.'
    lines = ['Reminder: the following application deadlines are approaching:']
    for drive in upcoming_drives:
        deadline = drive.application_deadline
        if deadline:
            lines.append(f"- {drive.title}: due {deadline.strftime('%Y-%m-%d %H:%M')}" )
        else:
            lines.append(f"- {drive.title}: deadline pending")
    lines.append('Please review the drive details soon and apply before the deadline.')
    return '\n'.join(lines)


def send_mail(to_email: str, subject: str, body: str, attachment_path: str | None = None) -> bool:
    smtp_host = os.getenv('SMTP_HOST')
    if not smtp_host:
        return False
    message = EmailMessage()
    message['Subject'] = subject
    message['To'] = to_email
    message['From'] = os.getenv('SMTP_FROM', 'placement-portal-support@example.com')
    message.set_content(body)
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as handle:
            data = handle.read()
        message.add_attachment(data, maintype='application', subtype='octet-stream', filename=os.path.basename(attachment_path))
    try:
        with smtplib.SMTP(smtp_host, int(os.getenv('SMTP_PORT', '25'))) as server:
            if os.getenv('SMTP_USE_TLS', 'true').lower() == 'true':
                server.starttls()
            username = os.getenv('SMTP_USERNAME')
            password = os.getenv('SMTP_PASSWORD')
            if username and password:
                server.login(username, password)
            server.send_message(message)
        return True
    except Exception:
        return False


def send_daily_reminders() -> dict:
    students = User.query.filter_by(role='student').all()
    upcoming = get_upcoming_deadlines(days_ahead=5)
    message_count = 0
    mails_sent = 0
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@institute.edu')
    if upcoming:
        message = build_reminder_message(upcoming)
    else:
        message = 'Reminder: please review the latest placement drives and application deadlines.'
    for student in students:
        if not student.email:
            continue
        message_count += 1
        if send_mail(student.email, 'Placement Reminder', message):
            mails_sent += 1
    if admin_email:
        send_mail(admin_email, 'Placement Reminder Summary', f'Sent email reminders to {mails_sent} students for {len(upcoming)} upcoming deadlines.')
    return {
        'checked_students': len(students),
        'upcoming_drives': len(upcoming),
        'message_count': message_count,
        'sent_via_email': mails_sent,
        'generated_at': datetime.utcnow().isoformat(),
    }
