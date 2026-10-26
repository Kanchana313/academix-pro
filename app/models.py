from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from app.database import Base

class Student(Base):
    """
    SQLAlchemy ORM model for storing student records.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Helper to serialize model instance to dictionary."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "date_of_birth": str(self.date_of_birth) if self.date_of_birth else None,
            "email": self.email,
            "phone": self.phone,
            "course": self.course,
            "address": self.address,
            "enrollment_date": str(self.enrollment_date) if self.enrollment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
