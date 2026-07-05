import os
from app import create_app
from models import db, User


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        # create admin if not exists
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@institute.edu")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "adminpass")
        if not User.query.filter_by(email=admin_email).first():
            u = User(name="Institute Admin", email=admin_email, role="admin")
            u.set_password(admin_pass)
            db.session.add(u)
            db.session.commit()
            print("Admin user created:", admin_email)
        else:
            print("Admin already exists")


if __name__ == "__main__":
    seed()
