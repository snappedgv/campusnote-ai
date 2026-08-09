"""
Seed script: creates an initial admin account and sample demo subjects
(Section 36). Run with:  python -m app.seed
"""
import sys
from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.subject import Subject, Unit
from app.auth.security import hash_password

DEMO_SUBJECTS = {
    "Database Management Systems": {
        "code": "CS3492",
        "department": "AI & Data Science",
        "semester": "4",
        "units": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"],
    },
    "Design and Analysis of Algorithms": {
        "code": "CS3401",
        "department": "AI & Data Science",
        "semester": "4",
        "units": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"],
    },
    "Operating Systems": {
        "code": "CS3451",
        "department": "AI & Data Science",
        "semester": "4",
        "units": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"],
    },
    "Computer Networks": {
        "code": "CS3591",
        "department": "AI & Data Science",
        "semester": "4",
        "units": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"],
    },
}


def run(admin_email="admin@campusnote.ai", admin_password="Admin@123", admin_name="Admin"):
    init_db()
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                name=admin_name,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            print(f"Created admin account: {admin_email} / {admin_password}  (CHANGE THIS PASSWORD)")
        else:
            print(f"Admin account already exists: {admin_email}")

        for name, info in DEMO_SUBJECTS.items():
            existing = db.query(Subject).filter(Subject.name == name).first()
            if existing:
                continue
            subject = Subject(name=name, code=info["code"], department=info["department"], semester=info["semester"])
            db.add(subject)
            db.flush()
            for i, unit_name in enumerate(info["units"]):
                db.add(Unit(subject_id=subject.id, name=unit_name, order_index=i))
            print(f"Created demo subject: {name}")

        db.commit()
        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
