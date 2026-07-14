import csv
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List

from models import Application, Company, Drive, User
from services.notifications import send_mail


def build_monthly_report_html() -> str:
    drives = Drive.query.order_by(Drive.id).all()
    applications = Application.query.order_by(Application.id).all()
    selected_count = sum(1 for app in applications if app.status == 'Selected')
    applied_count = len(applications)
    drive_count = len(drives)

    lines = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="utf-8">',
        '<title>Monthly Placement Activity Report</title>',
        '<style>body{font-family:Arial,sans-serif;padding:24px;}table{border-collapse:collapse;width:100%;margin-top:16px;}th,td{border:1px solid #ddd;padding:8px;text-align:left;}th{background:#f4f4f4;}</style>',
        '</head>',
        '<body>',
        '<h1>Monthly Placement Activity Report</h1>',
        f'<p>Generated on {date.today().strftime("%B %d, %Y")}</p>',
        '<h2>Summary</h2>',
        f'<ul><li>Drives conducted: {drive_count}</li><li>Students applied: {applied_count}</li><li>Students selected: {selected_count}</li></ul>',
        '<h2>Drive Breakdown</h2>',
        '<table>',
        '<thead><tr><th>Drive</th><th>Company</th><th>Status</th><th>Applications</th><th>Selections</th></tr></thead>',
        '<tbody>',
    ]

    for drive in drives:
        company = Company.query.get(drive.company_id)
        drive_applications = [app for app in applications if app.drive_id == drive.id]
        drive_selected = sum(1 for app in drive_applications if app.status == 'Selected')
        lines.append(
            f'<tr><td>{drive.title}</td><td>{company.name if company else "Unknown"}</td><td>{drive.status}</td><td>{len(drive_applications)}</td><td>{drive_selected}</td></tr>'
        )

    lines.extend(['</tbody>', '</table>', '</body>', '</html>'])
    return '\n'.join(lines)


def write_monthly_report_file(output_dir: str | None = None) -> str:
    output_dir = output_dir or os.environ.get('REPORT_DIR', '/tmp')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(output_dir, f"monthly_report_{int(datetime.utcnow().timestamp())}.html")
    with open(filename, 'w', encoding='utf-8') as handle:
        handle.write(build_monthly_report_html())
    recipient = os.getenv('ADMIN_EMAIL', 'admin@institute.edu')
    send_mail(recipient, 'Monthly Placement Activity Report', 'Please find the monthly placement activity report attached.', filename)
    return filename


def export_applications_csv_file(student_id: int, output_dir: str | None = None) -> str:
    output_dir = output_dir or os.environ.get('EXPORT_DIR', '/tmp')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(output_dir, f"applications_{student_id}_{int(datetime.utcnow().timestamp())}.csv")
    with open(filename, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['Application ID', 'Student ID', 'Company Name', 'Drive Title', 'Status', 'Applied On'])
        apps = Application.query.filter_by(student_id=student_id).all()
        for app in apps:
            drive = Drive.query.get(app.drive_id)
            company = Company.query.get(drive.company_id) if drive else None
            writer.writerow([
                app.id,
                app.student_id,
                company.name if company else '',
                drive.title if drive else '',
                app.status,
                app.applied_on.isoformat() if app.applied_on else '',
            ])
    return filename
