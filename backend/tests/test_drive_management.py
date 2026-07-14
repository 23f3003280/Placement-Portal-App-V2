import unittest

from app import create_app
from models import db


class CompanyDriveManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        )
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_company_can_edit_and_delete_created_drive(self):
        register_res = self.client.post('/api/register/company', json={
            'name': 'Acme Corp',
            'email': 'company@example.com',
            'password': 'secret123',
        })
        self.assertEqual(register_res.status_code, 201)

        login_res = self.client.post('/api/login', json={
            'email': 'company@example.com',
            'password': 'secret123',
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        create_res = self.client.post('/api/company/create_drive', headers=headers, json={
            'title': 'Software Engineer Drive',
            'description': 'Internship role',
            'eligibility': 'CGPA >= 7',
            'drive_date': '2026-07-15',
            'application_deadline': '2026-07-10T00:00:00',
        })
        self.assertEqual(create_res.status_code, 201)
        drive_id = create_res.get_json()['drive_id']

        edit_res = self.client.patch(f'/api/company/drives/{drive_id}', headers=headers, json={
            'title': 'Updated Drive',
            'description': 'Updated description',
            'eligibility': 'CGPA >= 8',
            'drive_date': '2026-08-01',
            'application_deadline': '2026-07-20T00:00:00',
        })
        self.assertEqual(edit_res.status_code, 200)

        list_res = self.client.get('/api/company/drives', headers=headers)
        self.assertEqual(list_res.status_code, 200)
        drives = list_res.get_json()
        self.assertEqual(len(drives), 1)
        self.assertEqual(drives[0]['title'], 'Updated Drive')
        self.assertEqual(drives[0]['drive_date'], '2026-08-01')

        delete_res = self.client.delete(f'/api/company/drives/{drive_id}', headers=headers)
        self.assertEqual(delete_res.status_code, 200)

        after_delete = self.client.get('/api/company/drives', headers=headers)
        self.assertEqual(after_delete.get_json(), [])

    def test_admin_can_update_drive_status_to_rejected(self):
        company = self.client.post('/api/register/company', json={
            'name': 'Acme Corp',
            'email': 'admincompany@example.com',
            'password': 'secret123',
        })
        self.assertEqual(company.status_code, 201)

        admin_login = self.client.post('/api/login', json={
            'email': 'admin@institute.edu',
            'password': 'adminpass',
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_token = admin_login.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        create_drive = self.client.post('/api/company/create_drive', headers={'Authorization': f'Bearer {self.client.post("/api/login", json={"email": "admincompany@example.com", "password": "secret123"}).get_json()["access_token"]}'}, json={
            'title': 'Summer Internship',
            'description': 'Role details',
            'eligibility': 'CGPA >= 7',
        })
        self.assertEqual(create_drive.status_code, 201)
        drive_id = create_drive.get_json()['drive_id']

        status_res = self.client.post(f'/api/admin/drives/{drive_id}/status', headers=admin_headers, json={'status': 'Rejected'})
        self.assertEqual(status_res.status_code, 200)

        list_res = self.client.get('/api/admin/drives', headers=admin_headers)
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(list_res.get_json()[0]['status'], 'Rejected')


if __name__ == '__main__':
    unittest.main()
