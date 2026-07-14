import os
import tempfile
import unittest

from app import create_app
from models import db, User, Company, Drive, Application
from tasks import generate_monthly_report, export_applications_csv


class ReportingTasksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            EXPORT_DIR=tempfile.gettempdir(),
            REPORT_DIR=tempfile.gettempdir(),
        )
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_generate_monthly_report_creates_html_file(self):
        student = User(name='Student', email='student@example.com', role='student')
        student.set_password('x')
        db.session.add(student)
        db.session.flush()
        company = Company(user_id=student.id, name='Acme', approved=True)
        db.session.add(company)
        db.session.flush()
        drive = Drive(company_id=company.id, title='Campus Drive', status='Approved')
        db.session.add(drive)
        db.session.flush()
        db.session.add(Application(student_id=student.id, drive_id=drive.id, status='Selected'))
        db.session.commit()

        result = generate_monthly_report()
        self.assertIn('path', result)
        self.assertTrue(os.path.exists(result['path']))
        with open(result['path'], 'r', encoding='utf-8') as handle:
            content = handle.read()
        self.assertIn('Monthly Placement Activity Report', content)
        self.assertIn('Campus Drive', content)

    def test_export_applications_csv_creates_file(self):
        student = User(name='Student', email='student@example.com', role='student')
        student.set_password('x')
        db.session.add(student)
        db.session.flush()
        company = Company(user_id=student.id, name='Acme', approved=True)
        db.session.add(company)
        db.session.flush()
        drive = Drive(company_id=company.id, title='Campus Drive', status='Approved')
        db.session.add(drive)
        db.session.flush()
        db.session.add(Application(student_id=student.id, drive_id=drive.id, status='Selected'))
        db.session.commit()

        result = export_applications_csv(student.id)
        self.assertIn('path', result)
        self.assertTrue(os.path.exists(result['path']))


if __name__ == '__main__':
    unittest.main()
