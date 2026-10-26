from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

class StudentBase(BaseModel):
    student_id: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique student identifier (e.g., STU1001, CS-2024-001)",
        examples=["STU1001"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the student",
        examples=["Aarav Sharma"]
    )
    date_of_birth: date = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        examples=["2003-08-15"]
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Contact email address (required if phone is not provided)",
        examples=["aarav.sharma@example.com"]
    )
    phone: Optional[str] = Field(
        None,
        max_length=30,
        description="Contact phone number (required if email is not provided)",
        examples=["+91-9876543210"]
    )
    course: Optional[str] = Field(
        None,
        max_length=100,
        description="Course or academic program",
        examples=["Computer Science"]
    )
    address: Optional[str] = Field(
        None,
        max_length=255,
        description="Residential address",
        examples=["42 MG Road, Bengaluru, Karnataka"]
    )
    enrollment_date: Optional[date] = Field(
        None,
        description="Enrollment date in YYYY-MM-DD format",
        examples=["2023-07-01"]
    )

    @model_validator(mode="after")
    def validate_contact_info(self):
        """Ensure that at least one contact method (email or phone) is provided."""
        has_email = self.email is not None and str(self.email).strip() != ""
        has_phone = self.phone is not None and str(self.phone).strip() != ""
        if not has_email and not has_phone:
            raise ValueError("At least one contact method (email and/or phone) must be provided.")
        return self


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student (PUT for full, PATCH for partial)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    model_config = ConfigDict(extra="forbid")


class StudentResponse(BaseModel):
    """Schema for returning student data in API responses."""
    id: int
    student_id: str
    name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """Paginated or filtered list of student records."""
    total: int
    count: int
    skip: int
    limit: int
    students: List[StudentResponse]


class AIQueryRequest(BaseModel):
    """Request payload for Ollama natural-language student data query."""
    question: str = Field(
        ...,
        min_length=3,
        description="Natural language question about student records (e.g. 'How many students are there?' or 'List students born after 2005')",
        examples=["How many students are enrolled in Computer Science?"]
    )
    model: Optional[str] = Field(
        None,
        description="Ollama model name to query (defaults to configured model, e.g. llama3.2:1b)"
    )


class AIQueryResponse(BaseModel):
    """Structured response from the Ollama AI extension with grounded context."""
    question: str
    answer: str
    records_referenced: int
    matched_records_preview: List[dict]
    source: str = Field(..., description="'ollama' or 'backend_grounded_fallback'")
    model_used: Optional[str] = None
