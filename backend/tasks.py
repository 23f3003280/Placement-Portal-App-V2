from celery_worker import celery
from app import create_app
from services.notifications import send_daily_reminders as notify_students
from services.reporting import export_applications_csv_file, write_monthly_report_file

app = create_app()


@celery.task(name="tasks.export_applications_csv")
def export_applications_csv(student_id: int):
    with app.app_context():
        path = export_applications_csv_file(student_id, output_dir=app.config.get('EXPORT_DIR'))
    return {"path": path}


@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    with app.app_context():
        summary = notify_students()
    return summary


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    with app.app_context():
        path = write_monthly_report_file(output_dir=app.config.get('REPORT_DIR'))
    return {"path": path}
