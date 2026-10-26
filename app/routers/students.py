from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/students", tags=["Students"])

@router.post(
    "",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Add a new student record to the SQLite database. Requires unique student_id and at least one contact info (email or phone)."
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    # Check if student_id already exists
    existing = crud.get_student_by_id(db, student_id=student_in.student_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with ID '{student_in.student_id}' already exists."
        )

    # Check if email is already taken by another student (if email provided)
    if student_in.email:
        existing_email = crud.get_student_by_email(db, email=str(student_in.email).lower())
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with email '{student_in.email}' already exists."
            )

    try:
        new_student = crud.create_student(db, student=student_in)
        return new_student
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the student record: {str(e)}"
        )


@router.get(
    "",
    response_model=schemas.StudentListResponse,
    summary="List or filter students",
    description="Retrieve all students with optional search, course filtering, birth date filtering, and pagination."
)
def list_students(
    search: Optional[str] = Query(None, description="Search by name, student ID, email, or phone"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    born_after: Optional[date] = Query(None, description="Filter students born after date (YYYY-MM-DD)"),
    born_before: Optional[date] = Query(None, description="Filter students born before date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db)
):
    students, total = crud.get_students(
        db,
        skip=skip,
        limit=limit,
        search=search,
        course=course,
        born_after=born_after,
        born_before=born_before
    )
    return schemas.StudentListResponse(
        total=total,
        count=len(students),
        skip=skip,
        limit=limit,
        students=students
    )


@router.get(
    "/stats/summary",
    summary="Get database stats summary",
    description="Returns aggregate statistics like total student count and course distribution."
)
def get_students_summary(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    summary="View a student profile",
    description="Retrieve individual student profile details by unique student_id."
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    summary="Full update of student details",
    description="Modify all editable details of an existing student."
)
def update_student_full(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = crud.update_student(
            db,
            student_id=student_id,
            student_update=student_update,
            partial=False
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return updated


@router.patch(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    summary="Partial update of student details",
    description="Modify specific fields of an existing student record."
)
def update_student_partial(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = crud.update_student(
            db,
            student_id=student_id,
            student_update=student_update,
            partial=True
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return updated


@router.delete(
    "/{student_id}",
    summary="Delete a student",
    description="Remove a student record permanently from the SQLite database."
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    success = crud.delete_student(db, student_id=student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return {
        "status": "success",
        "message": f"Student with ID '{student_id}' was successfully deleted."
    }
