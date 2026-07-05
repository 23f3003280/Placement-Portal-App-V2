from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # admin, company, student
    profile = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    blacklisted = db.Column(db.Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    hr_contact = db.Column(db.String(128), nullable=True)
    website = db.Column(db.String(256), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    extra = db.Column(db.JSON, nullable=True)


class Drive(db.Model):
    __tablename__ = "drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligibility = db.Column(db.JSON, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(32), default="Pending")  # Pending / Approved / Closed
    extra = db.Column(db.JSON, nullable=True)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drives.id"), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), default="Applied")  # Applied / Shortlisted / Selected / Rejected
    extra = db.Column(db.JSON, nullable=True)
