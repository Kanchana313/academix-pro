"""
Seed sample dummy student records into the SQLite database.
Safe dummy data with no real student personal information.
"""
from datetime import date
from app.database import SessionLocal, Base, engine
from app import models

SAMPLE_STUDENTS = [
    {
        "student_id": "STU1001",
        "name": "Aarav Sharma",
        "date_of_birth": date(2003, 5, 14),
        "email": "aarav.sharma@example.com",
        "phone": "+91-9876543210",
        "course": "Computer Science",
        "address": "42 MG Road, Bengaluru, Karnataka",
        "enrollment_date": date(2022, 8, 1)
    },
    {
        "student_id": "STU1002",
        "name": "Diya Patel",
        "date_of_birth": date(2004, 11, 22),
        "email": "diya.patel@example.com",
        "phone": "+91-9823456789",
        "course": "Data Science",
        "address": "15 Ashram Road, Ahmedabad, Gujarat",
        "enrollment_date": date(2023, 7, 15)
    },
    {
        "student_id": "STU1003",
        "name": "Rohan Verma",
        "date_of_birth": date(2002, 3, 10),
        "email": "rohan.verma@example.com",
        "phone": "+91-9123456780",
        "course": "Artificial Intelligence",
        "address": "78 Park Street, Kolkata, West Bengal",
        "enrollment_date": date(2021, 9, 10)
    },
    {
        "student_id": "STU1004",
        "name": "Ananya Iyer",
        "date_of_birth": date(2006, 1, 18),
        "email": "ananya.iyer@example.com",
        "phone": "+91-9445566778",
        "course": "Computer Science",
        "address": "12 Anna Salai, Chennai, Tamil Nadu",
        "enrollment_date": date(2024, 7, 20)
    },
    {
        "student_id": "STU1005",
        "name": "Kabir Mehta",
        "date_of_birth": date(2005, 9, 30),
        "email": "kabir.mehta@example.com",
        "phone": "+91-9765432109",
        "course": "Information Technology",
        "address": "90 Bandra West, Mumbai, Maharashtra",
        "enrollment_date": date(2023, 8, 5)
    },
    {
        "student_id": "STU1006",
        "name": "Sneha Kulkarni",
        "date_of_birth": date(2007, 4, 12),
        "email": "sneha.k@example.com",
        "phone": "+91-9890123456",
        "course": "Artificial Intelligence",
        "address": "23 FC Road, Pune, Maharashtra",
        "enrollment_date": date(2025, 1, 10)
    },
    {
        "student_id": "STU1007",
        "name": "Vikram Singh",
        "date_of_birth": date(2003, 12, 5),
        "email": "vikram.singh@example.com",
        "phone": "+91-9811223344",
        "course": "Cyber Security",
        "address": "56 MI Road, Jaipur, Rajasthan",
        "enrollment_date": date(2022, 8, 15)
    },
    {
        "student_id": "STU1008",
        "name": "Meera Nair",
        "date_of_birth": date(2006, 8, 25),
        "email": "meera.nair@example.com",
        "phone": "+91-9495123456",
        "course": "Data Science",
        "address": "34 Marine Drive, Kochi, Kerala",
        "enrollment_date": date(2024, 8, 1)
    }
]

def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted = 0
        for data in SAMPLE_STUDENTS:
            existing = db.query(models.Student).filter(models.Student.student_id == data["student_id"]).first()
            if not existing:
                student = models.Student(**data)
                db.add(student)
                inserted += 1
        db.commit()
        print(f"Successfully seeded {inserted} dummy student records into SQLite database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
