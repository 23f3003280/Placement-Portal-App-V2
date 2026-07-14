import unittest

from app import create_app
from models import db


class AdminDriveReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_admin_can_fetch_drive_review_details_with_applicants(self):
        company_res = self.client.post('/api/register/company', json={
            'name': 'Acme Corp',
            'email': 'company@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_res.status_code, 201)

        student_res = self.client.post('/api/register/student', json={
            'name': 'Jane Student',
            'email': 'student@example.com',
            'password': 'secret123',
        })
        self.assertEqual(student_res.status_code, 201)

        admin_login = self.client.post('/api/login', json={
            'email': 'admin@institute.edu',
            'password': 'adminpass',
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_token = admin_login.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        company_login = self.client.post('/api/login', json={
            'email': 'company@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_login.status_code, 200)
        company_headers = {'Authorization': f'Bearer {company_login.get_json()["access_token"]}'}

        create_drive = self.client.post('/api/company/create_drive', headers=company_headers, json={
            'title': 'Software Engineer',
            'description': 'Build software',
            'eligibility': 'CGPA >= 7',
            'drive_date': '2026-07-15',
            'application_deadline': '2026-07-10T00:00:00',
        })
        self.assertEqual(create_drive.status_code, 201)
        drive_id = create_drive.get_json()['drive_id']

        self.client.post(f'/api/admin/drives/{drive_id}/status', headers=admin_headers, json={'status': 'Approved'})

        student_login = self.client.post('/api/login', json={
            'email': 'student@example.com',
            'password': 'secret123',
        })
        self.assertEqual(student_login.status_code, 200)
        student_headers = {'Authorization': f'Bearer {student_login.get_json()["access_token"]}'}

        apply_res = self.client.post(f'/api/drives/{drive_id}/apply', headers=student_headers)
        self.assertEqual(apply_res.status_code, 201)

        details_res = self.client.get(f'/api/admin/drives/{drive_id}/details', headers=admin_headers)
        self.assertEqual(details_res.status_code, 200)
        payload = details_res.get_json()
        self.assertEqual(payload['drive']['id'], drive_id)
        self.assertEqual(len(payload['applicants']), 1)
        self.assertEqual(payload['applicants'][0]['student_name'], 'Jane Student')

    def test_drive_details_endpoint_includes_company_profile(self):
        company_res = self.client.post('/api/register/company', json={
            'name': 'Nova Labs',
            'email': 'nova@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_res.status_code, 201)

        company_login = self.client.post('/api/login', json={
            'email': 'nova@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_login.status_code, 200)
        company_headers = {'Authorization': f'Bearer {company_login.get_json()["access_token"]}'}

        create_drive = self.client.post('/api/company/create_drive', headers=company_headers, json={
            'title': 'Data Analyst',
            'description': 'Work with data',
            'eligibility': 'CGPA >= 6',
            'drive_date': '2026-07-20',
            'application_deadline': '2026-07-15T00:00:00',
        })
        self.assertEqual(create_drive.status_code, 201)
        drive_id = create_drive.get_json()['drive_id']

        admin_login = self.client.post('/api/login', json={
            'email': 'admin@institute.edu',
            'password': 'adminpass',
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_headers = {'Authorization': f'Bearer {admin_login.get_json()["access_token"]}'}
        self.client.post(f'/api/admin/drives/{drive_id}/status', headers=admin_headers, json={'status': 'Approved'})

        details_res = self.client.get(f'/api/drives/{drive_id}/details')
        self.assertEqual(details_res.status_code, 200)
        payload = details_res.get_json()
        self.assertEqual(payload['drive']['title'], 'Data Analyst')
        self.assertEqual(payload['company']['name'], 'Nova Labs')
        self.assertEqual(payload['company']['approved'], False)

    def test_student_notifications_include_drive_and_application_updates(self):
        company_res = self.client.post('/api/register/company', json={
            'name': 'Northwind',
            'email': 'northwind@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_res.status_code, 201)

        student_res = self.client.post('/api/register/student', json={
            'name': 'Ava Student',
            'email': 'ava@example.com',
            'password': 'secret123',
        })
        self.assertEqual(student_res.status_code, 201)

        student_login = self.client.post('/api/login', json={
            'email': 'ava@example.com',
            'password': 'secret123',
        })
        self.assertEqual(student_login.status_code, 200)
        student_token = student_login.get_json()['access_token']
        student_headers = {'Authorization': f'Bearer {student_token}'}

        company_login = self.client.post('/api/login', json={
            'email': 'northwind@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company_login.status_code, 200)
        company_headers = {'Authorization': f'Bearer {company_login.get_json()["access_token"]}'}

        create_drive = self.client.post('/api/company/create_drive', headers=company_headers, json={
            'title': 'Cloud Engineer',
            'description': 'Build cloud systems',
            'eligibility': 'CGPA >= 7',
            'drive_date': '2026-07-25',
            'application_deadline': '2026-07-20T00:00:00',
        })
        self.assertEqual(create_drive.status_code, 201)
        drive_id = create_drive.get_json()['drive_id']

        admin_login = self.client.post('/api/login', json={
            'email': 'admin@institute.edu',
            'password': 'adminpass',
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_headers = {'Authorization': f'Bearer {admin_login.get_json()["access_token"]}'}
        self.client.post(f'/api/admin/drives/{drive_id}/status', headers=admin_headers, json={'status': 'Approved'})

        apply_res = self.client.post(f'/api/drives/{drive_id}/apply', headers=student_headers)
        self.assertEqual(apply_res.status_code, 201)

        notifications_res = self.client.get('/api/notifications', headers=student_headers)
        self.assertEqual(notifications_res.status_code, 200)
        payload = notifications_res.get_json()
        self.assertTrue(any(item.get('title') == 'Drive Update' for item in payload))
        self.assertTrue(any('approved' in item.get('message', '').lower() for item in payload))


if __name__ == '__main__':
    unittest.main()
