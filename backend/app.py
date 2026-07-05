from datetime import datetime
from pathlib import Path
from time import time

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from models import db, User, Company, Drive, Application
from services.notifications import send_daily_reminders
from services.reporting import export_applications_csv_file, write_monthly_report_file

jwt = JWTManager()
CACHE_TTL_SECONDS = 30
_cache = {}


def _cache_get(key: str):
    entry = _cache.get(key)
    if not entry:
        return None
    value, expires_at = entry
    if time() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value, ttl: int = CACHE_TTL_SECONDS):
    _cache[key] = (value, time() + ttl)
    return value


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'change-this-in-prod'
    app.config['EXPORT_DIR'] = Path('instance/exports')
    app.config['REPORT_DIR'] = Path('instance/reports')

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    @app.route('/api/register/student', methods=['POST'])
    def register_student():
        data = request.get_json() or {}
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'message': 'name, email, password required'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'email already registered'}), 400
        u = User(name=data['name'], email=data['email'], role='student')
        u.set_password(data['password'])
        db.session.add(u)
        db.session.commit()
        return jsonify({'message': 'student registered'}), 201

    @app.route('/api/register/company', methods=['POST'])
    def register_company():
        data = request.get_json() or {}
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'message': 'name, email, password required'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'email already registered'}), 400
        user = User(name=data.get('contact_name') or data['name'], email=data['email'], role='company', is_active=True)
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        company = Company(user_id=user.id, name=data['name'], hr_contact=data.get('hr_contact'), website=data.get('website'))
        db.session.add(company)
        db.session.commit()
        return jsonify({'message': 'company registered, pending admin approval', 'company_id': company.id}), 201

    def create_user_registration(data):
        if not data.get('email') or not data.get('password') or not data.get('name') or not data.get('role'):
            return jsonify({'message': 'name, email, password, role required'}), 400
        if data.get('role') not in ('student', 'company'):
            return jsonify({'message': 'role must be student or company'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'email already registered'}), 400
        role = data['role']
        user = User(name=data['name'], email=data['email'], role=role, is_active=(role == 'student' or role == 'company'))
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        if role == 'company':
            company = Company(user_id=user.id, name=data['name'], hr_contact=data.get('hr_contact'), website=data.get('website'))
            db.session.add(company)
            db.session.commit()
            return jsonify({'message': 'company registered, pending admin approval', 'company_id': company.id}), 201
        return jsonify({'message': 'student registered'}), 201

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        return create_user_registration(data)

    def admin_required():
        if get_jwt().get('role') != 'admin':
            return jsonify({'message': 'admin access required'}), 403

    def get_current_user():
        user_id = get_jwt_identity()
        if user_id is None:
            return None
        return User.query.get(int(user_id))

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'message': 'email and password required'}), 400
        u = User.query.filter_by(email=email).first()
        if not u or not u.check_password(password):
            return jsonify({'message': 'invalid credentials'}), 401
        if u.blacklisted:
            return jsonify({'message': 'account disabled'}), 403
        if u.role != 'company' and not u.is_active:
            return jsonify({'message': 'account disabled'}), 403
        if u.role == 'company':
            company = Company.query.filter_by(user_id=u.id).first()
            if not company:
                return jsonify({'message': 'company profile not found'}), 404
        token = create_access_token(identity=str(u.id), additional_claims={'role': u.role})
        return jsonify({'access_token': token, 'role': u.role}), 200

    @app.route('/api/me', methods=['GET'])
    @jwt_required()
    def get_profile():
        u = get_current_user()
        if not u:
            return jsonify({'message': 'user not found'}), 404
        out = {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'blacklisted': u.blacklisted,
            'profile': u.profile or {},
        }
        if u.role == 'company':
            company = Company.query.filter_by(user_id=u.id).first()
            if company:
                out['company'] = {
                    'id': company.id,
                    'name': company.name,
                    'approved': company.approved,
                    'hr_contact': company.hr_contact,
                    'website': company.website,
                }
        return jsonify(out)

    @app.route('/api/me', methods=['POST'])
    @jwt_required()
    def update_profile():
        data = request.get_json() or {}
        u = get_current_user()
        if not u:
            return jsonify({'message': 'user not found'}), 404
        if data.get('name'):
            u.name = data['name']
        profile = u.profile or {}
        for field in ('phone', 'bio', 'education', 'skills'):
            if field in data:
                profile[field] = data[field]
        u.profile = profile
        db.session.commit()
        return jsonify({'message': 'profile updated'})

    @app.route('/api/me/resume', methods=['POST'])
    @jwt_required()
    def upload_resume():
        if 'resume' not in request.files:
            return jsonify({'message': 'resume file required'}), 400
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'message': 'resume file required'}), 400
        u = get_current_user()
        if not u:
            return jsonify({'message': 'user not found'}), 404
        resume_dir = Path('instance/resumes')
        resume_dir.mkdir(parents=True, exist_ok=True)
        filename = secure_filename(f"{u.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
        filepath = resume_dir / filename
        file.save(filepath)
        profile = u.profile or {}
        profile['resume_file'] = filename
        u.profile = profile
        db.session.commit()
        return jsonify({'message': 'resume uploaded', 'resume_file': filename})

    @app.route('/api/me/resume', methods=['GET'])
    @jwt_required()
    def get_resume():
        u = get_current_user()
        if not u:
            return jsonify({'message': 'user not found'}), 404
        profile = u.profile or {}
        filename = profile.get('resume_file')
        if not filename:
            return jsonify({'message': 'no resume uploaded'}), 404
        return send_from_directory('instance/resumes', filename, as_attachment=True)

    @app.route('/api/company/drives', methods=['GET'])
    @jwt_required()
    def get_company_drives():
        if get_jwt().get('role') != 'company':
            return jsonify({'message': 'company access required'}), 403
        user = get_current_user()
        comp = Company.query.filter_by(user_id=user.id).first()
        if not comp:
            return jsonify({'message': 'company not found'}), 404
        drives = Drive.query.filter_by(company_id=comp.id).all()
        out = []
        for d in drives:
            app_count = Application.query.filter_by(drive_id=d.id).count()
            out.append({
                'drive_id': d.id,
                'title': d.title,
                'description': d.description,
                'eligibility': d.eligibility,
                'status': d.status,
                'applicant_count': app_count,
            })
        return jsonify(out)

    @app.route('/api/company/applications', methods=['GET'])
    @jwt_required()
    def get_company_applications():
        if get_jwt().get('role') != 'company':
            return jsonify({'message': 'company access required'}), 403
        user = get_current_user()
        comp = Company.query.filter_by(user_id=user.id).first()
        if not comp:
            return jsonify({'message': 'company not found'}), 404
        drive_ids = [d.id for d in Drive.query.filter_by(company_id=comp.id).all()]
        if not drive_ids:
            return jsonify([])
        apps = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
        out = []
        for a in apps:
            student = User.query.get(a.student_id)
            drive = Drive.query.get(a.drive_id)
            out.append({
                'application_id': a.id,
                'student_id': a.student_id,
                'student_name': student.name if student else None,
                'email': student.email if student else None,
                'drive_id': a.drive_id,
                'drive_title': drive.title if drive else None,
                'status': a.status,
                'applied_on': a.applied_on.isoformat() if a.applied_on else None,
            })
        return jsonify(out)

    @app.route('/api/applications/<int:application_id>/status', methods=['PATCH'])
    @jwt_required()
    def update_application_status(application_id):
        data = request.get_json() or {}
        status = data.get('status')
        if status not in ('Applied', 'Shortlisted', 'Selected', 'Rejected'):
            return jsonify({'message': 'invalid status'}), 400
        apprec = Application.query.get(application_id)
        if not apprec:
            return jsonify({'message': 'application not found'}), 404
        current_role = get_jwt().get('role')
        user = get_current_user()
        if current_role == 'company':
            comp = Company.query.filter_by(user_id=user.id).first()
            if not comp:
                return jsonify({'message': 'company not found'}), 404
            drive = Drive.query.get(apprec.drive_id)
            if not drive or drive.company_id != comp.id:
                return jsonify({'message': 'access denied'}), 403
        elif current_role != 'admin':
            return jsonify({'message': 'access denied'}), 403
        apprec.status = status
        db.session.commit()
        return jsonify({'message': 'application status updated'})

    @app.route('/api/admin/approve_company/<int:company_id>', methods=['POST'])
    @jwt_required()
    def approve_company(company_id):
        err = admin_required()
        if err:
            return err
        c = Company.query.get(company_id)
        if not c:
            return jsonify({'message': 'company not found'}), 404
        c.approved = True
        user = User.query.get(c.user_id)
        if user:
            user.is_active = True
        db.session.commit()
        return jsonify({'message': 'company approved'}), 200

    @app.route('/api/admin/reject_company/<int:company_id>', methods=['POST'])
    @jwt_required()
    def reject_company(company_id):
        err = admin_required()
        if err:
            return err
        c = Company.query.get(company_id)
        if not c:
            return jsonify({'message': 'company not found'}), 404
        c.approved = False
        user = User.query.get(c.user_id)
        if user:
            user.is_active = False
        db.session.commit()
        return jsonify({'message': 'company rejected'}), 200

    @app.route('/api/admin/companies', methods=['GET'])
    @jwt_required()
    def admin_list_companies():
        err = admin_required()
        if err:
            return err
        q = request.args.get('q', '').strip()
        query = Company.query.join(User, Company.user_id == User.id)
        if q:
            query = query.filter(or_(Company.name.ilike(f'%{q}%'), User.email.ilike(f'%{q}%')))
        companies = query.all()
        out = []
        for c in companies:
            user = User.query.get(c.user_id)
            out.append({
                'company_id': c.id,
                'user_id': c.user_id,
                'name': c.name,
                'email': user.email if user else None,
                'approved': c.approved,
                'is_active': user.is_active if user else False,
                'blacklisted': user.blacklisted if user else False,
                'hr_contact': c.hr_contact,
                'website': c.website,
            })
        return jsonify(out)

    @app.route('/api/admin/students', methods=['GET'])
    @jwt_required()
    def admin_list_students():
        err = admin_required()
        if err:
            return err
        q = request.args.get('q', '').strip()
        query = User.query.filter_by(role='student')
        if q:
            query = query.filter(or_(User.name.ilike(f'%{q}%'), User.email.ilike(f'%{q}%')))
        students = query.all()
        out = []
        for s in students:
            out.append({
                'student_id': s.id,
                'name': s.name,
                'email': s.email,
                'is_active': s.is_active,
                'blacklisted': s.blacklisted,
            })
        return jsonify(out)

    @app.route('/api/admin/drives', methods=['GET'])
    @jwt_required()
    def admin_list_drives():
        err = admin_required()
        if err:
            return err
        q = request.args.get('q', '').strip()
        query = Drive.query
        if q:
            query = query.filter(Drive.title.ilike(f'%{q}%'))
        drives = query.all()
        out = []
        for d in drives:
            company = Company.query.get(d.company_id)
            out.append({
                'drive_id': d.id,
                'company_id': d.company_id,
                'company_name': company.name if company else None,
                'title': d.title,
                'description': d.description,
                'eligibility': d.eligibility,
                'status': d.status,
            })
        return jsonify(out)

    @app.route('/api/admin/drives/<int:drive_id>/approve', methods=['POST'])
    @jwt_required()
    def approve_drive_admin(drive_id):
        err = admin_required()
        if err:
            return err
        drive = Drive.query.get(drive_id)
        if not drive:
            return jsonify({'message': 'drive not found'}), 404
        drive.status = 'Approved'
        db.session.commit()
        return jsonify({'message': 'drive approved'}), 200

    @app.route('/api/admin/drives/<int:drive_id>/reject', methods=['POST'])
    @jwt_required()
    def reject_drive_admin(drive_id):
        err = admin_required()
        if err:
            return err
        drive = Drive.query.get(drive_id)
        if not drive:
            return jsonify({'message': 'drive not found'}), 404
        drive.status = 'Closed'
        db.session.commit()
        return jsonify({'message': 'drive rejected'}), 200

    @app.route('/api/admin/users/<int:user_id>/blacklist', methods=['POST'])
    @jwt_required()
    def blacklist_user(user_id):
        err = admin_required()
        if err:
            return err
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'user not found'}), 404
        user.blacklisted = True
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'user blacklisted'}), 200

    @app.route('/api/admin/users/<int:user_id>/deactivate', methods=['POST'])
    @jwt_required()
    def deactivate_user(user_id):
        err = admin_required()
        if err:
            return err
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'user not found'}), 404
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'user deactivated'}), 200

    @app.route('/api/admin/users/<int:user_id>/activate', methods=['POST'])
    @jwt_required()
    def activate_user(user_id):
        err = admin_required()
        if err:
            return err
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'user not found'}), 404
        user.is_active = True
        user.blacklisted = False
        db.session.commit()
        return jsonify({'message': 'user activated'}), 200

    @app.route('/api/admin/summary', methods=['GET'])
    @jwt_required()
    def admin_summary():
        err = admin_required()
        if err:
            return err
        cached = _cache_get('admin-summary')
        if cached is not None:
            return jsonify(cached)
        students_count = User.query.filter_by(role='student').count()
        companies_count = User.query.filter_by(role='company').count()
        drives_count = Drive.query.count()
        pending_companies = Company.query.filter_by(approved=False).count()
        pending_drives = Drive.query.filter_by(status='Pending').count()
        data = {
            'total_students': students_count,
            'total_companies': companies_count,
            'total_drives': drives_count,
            'pending_companies': pending_companies,
            'pending_drives': pending_drives,
        }
        return jsonify(_cache_set('admin-summary', data))

    @app.route('/api/company/create_drive', methods=['POST'])
    @jwt_required()
    def create_drive():
        if get_jwt().get('role') != 'company':
            return jsonify({'message': 'company access required'}), 403
        user_id = get_jwt_identity()
        comp = Company.query.filter_by(user_id=user_id).first()
        if not comp:
            return jsonify({'message': 'company not found'}), 404
        data = request.get_json() or {}
        d = Drive(company_id=comp.id, title=data.get('title'), description=data.get('description'), eligibility=data.get('eligibility', {}), status='Pending', application_deadline=data.get('application_deadline'))
        db.session.add(d)
        db.session.commit()
        return jsonify({'message': 'drive created, pending admin approval', 'drive_id': d.id}), 201

    @app.route('/api/drives', methods=['GET'])
    def list_drives():
        cached = _cache_get('drives-list')
        if cached is not None:
            return jsonify(cached)
        q = request.args.get('q', '').strip()
        query = Drive.query.filter_by(status='Approved')
        if q:
            query = query.filter(or_(Drive.title.ilike(f'%{q}%'), Drive.description.ilike(f'%{q}%')))
        drives = query.all()
        out = []
        for d in drives:
            if q and d.eligibility:
                eligibility_text = ' '.join(str(v) for v in (d.eligibility or {}).values())
                if q.lower() not in eligibility_text.lower() and q.lower() not in d.title.lower() and q.lower() not in (d.description or '').lower():
                    continue
            company = Company.query.get(d.company_id)
            out.append({'id': d.id, 'company_id': d.company_id, 'company_name': company.name if company else None, 'title': d.title, 'description': d.description, 'eligibility': d.eligibility, 'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None})
        return jsonify(_cache_set('drives-list', out))

    @app.route('/api/drives/<int:drive_id>/apply', methods=['POST'])
    @jwt_required()
    def apply_drive(drive_id):
        if get_jwt().get('role') != 'student':
            return jsonify({'message': 'student access required'}), 403
        student_id = get_jwt_identity()
        drive = Drive.query.get(drive_id)
        if not drive or drive.status != 'Approved':
            return jsonify({'message': 'drive not open'}), 400
        if Application.query.filter_by(student_id=student_id, drive_id=drive_id).first():
            return jsonify({'message': 'already applied'}), 400
        apprec = Application(student_id=student_id, drive_id=drive_id)
        db.session.add(apprec)
        db.session.commit()
        _cache.pop('drives-list', None)
        return jsonify({'message': 'applied'}), 201

    @app.route('/api/applications', methods=['GET'])
    @jwt_required()
    def get_applications():
        role = get_jwt().get('role')
        user_id = get_jwt_identity()
        if role == 'student':
            apps = Application.query.filter_by(student_id=user_id).all()
        elif role == 'company':
            comp = Company.query.filter_by(user_id=user_id).first()
            drive_ids = [d.id for d in Drive.query.filter_by(company_id=comp.id).all()] if comp else []
            apps = Application.query.filter(Application.drive_id.in_(drive_ids)).all() if drive_ids else []
        else:
            apps = Application.query.all()
        out = []
        for a in apps:
            drive = Drive.query.get(a.drive_id)
            company = Company.query.get(drive.company_id) if drive else None
            student = User.query.get(a.student_id)
            out.append({
                'id': a.id,
                'student_id': a.student_id,
                'student_name': student.name if student else None,
                'drive_id': a.drive_id,
                'drive_title': drive.title if drive else None,
                'company_name': company.name if company else None,
                'status': a.status,
                'applied_on': a.applied_on.isoformat() if a.applied_on else None,
            })
        return jsonify(out)

    @app.route('/api/student/export-applications', methods=['POST'])
    @jwt_required()
    def export_applications():
        if get_jwt().get('role') != 'student':
            return jsonify({'message': 'student access required'}), 403
        student_id = int(get_jwt_identity())
        output_dir = app.config.get('EXPORT_DIR')
        export_path = export_applications_csv_file(student_id, output_dir=str(output_dir))
        return jsonify({'message': 'Export started', 'path': export_path})

    @app.route('/api/admin/report/monthly', methods=['GET'])
    @jwt_required()
    def monthly_report():
        err = admin_required()
        if err:
            return err
        output_dir = app.config.get('REPORT_DIR')
        report_path = write_monthly_report_file(output_dir=str(output_dir))
        return jsonify({'message': 'Report generated', 'path': report_path})

    @app.route('/api/admin/notifications/reminders', methods=['POST'])
    @jwt_required()
    def trigger_reminders():
        err = admin_required()
        if err:
            return err
        summary = send_daily_reminders()
        return jsonify(summary)

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@institute.edu').first():
            admin = User(name='Institute Admin', email='admin@institute.edu', role='admin')
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)
