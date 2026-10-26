from datetime import date, datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app import models, schemas

def get_student_by_id(db: Session, student_id: str) -> Optional[models.Student]:
    """Retrieve a single student record by unique student_id."""
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()

def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    """Retrieve a student by email address if needed for uniqueness check."""
    if not email:
        return None
    return db.query(models.Student).filter(models.Student.email == email).first()

def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None
) -> Tuple[List[models.Student], int]:
    """
    List students with flexible search and filtering.
    Returns (students, total_count).
    """
    query = db.query(models.Student)

    # Filter by search string (matches name, student_id, email, phone)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Student.name.ilike(search_pattern),
                models.Student.student_id.ilike(search_pattern),
                models.Student.email.ilike(search_pattern),
                models.Student.phone.ilike(search_pattern),
            )
        )

    # Filter by specific course
    if course:
        query = query.filter(models.Student.course.ilike(f"%{course.strip()}%"))

    # Filter by birth date range
    if born_after:
        query = query.filter(models.Student.date_of_birth > born_after)
    if born_before:
        query = query.filter(models.Student.date_of_birth < born_before)

    total_count = query.count()
    students = query.order_by(models.Student.id.desc()).offset(skip).limit(limit).all()

    return students, total_count

def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    """Create a new student record."""
    db_student = models.Student(
        student_id=student.student_id.strip(),
        name=student.name.strip(),
        date_of_birth=student.date_of_birth,
        email=str(student.email).strip().lower() if student.email else None,
        phone=student.phone.strip() if student.phone else None,
        course=student.course.strip() if student.course else None,
        address=student.address.strip() if student.address else None,
        enrollment_date=student.enrollment_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(
    db: Session,
    student_id: str,
    student_update: schemas.StudentUpdate,
    partial: bool = False
) -> Optional[models.Student]:
    """
    Update an existing student's details.
    - partial=True: only set provided fields (PATCH)
    - partial=False: full replacement of editable fields (PUT)
    """
    db_student = get_student_by_id(db, student_id=student_id)
    if not db_student:
        return None

    update_data = student_update.model_dump(exclude_unset=partial)

    # Ensure we don't accidentally leave both email and phone blank
    new_email = update_data.get("email", db_student.email)
    new_phone = update_data.get("phone", db_student.phone)
    if not new_email and not new_phone:
        raise ValueError("Cannot update student: At least one contact method (email or phone) must remain.")

    for field, value in update_data.items():
        if field == "email" and value:
            value = str(value).strip().lower()
        elif isinstance(value, str):
            value = value.strip()
        setattr(db_student, field, value)

    db_student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: str) -> bool:
    """Delete a student record by student_id."""
    db_student = get_student_by_id(db, student_id=student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True

def get_stats(db: Session) -> Dict[str, Any]:
    """Get aggregate statistics for the dashboard and AI context."""
    total_students = db.query(models.Student).count()
    courses = db.query(
        models.Student.course,
        func.count(models.Student.id)
    ).group_by(models.Student.course).all()

    course_distribution = {c[0] or "Unassigned": c[1] for c in courses}
    return {
        "total_students": total_students,
        "courses_count": len(course_distribution),
        "course_distribution": course_distribution,
    }
