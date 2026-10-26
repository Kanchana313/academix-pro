import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh database schema before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_student_success(client):
    """Test creating a new student record successfully."""
    payload = {
        "student_id": "STU_TEST_01",
        "name": "Arjun Patel",
        "date_of_birth": "2004-06-15",
        "email": "arjun.patel@example.com",
        "phone": "+91-9988776655",
        "course": "Computer Science",
        "address": "100 MG Road",
        "enrollment_date": "2023-08-01"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU_TEST_01"
    assert data["name"] == "Arjun Patel"
    assert data["email"] == "arjun.patel@example.com"
    assert "id" in data


def test_create_student_duplicate_id_fails(client):
    """Test that creating a student with an already existing ID returns 400 Bad Request."""
    payload = {
        "student_id": "STU_DUP_01",
        "name": "Student One",
        "date_of_birth": "2003-01-01",
        "email": "one@example.com"
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate
    res2 = client.post("/students", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_create_student_missing_both_contact_methods_fails(client):
    """Test that creating a student without email or phone is rejected by validation."""
    payload = {
        "student_id": "STU_NO_CONTACT",
        "name": "No Contact Student",
        "date_of_birth": "2003-01-01"
        # Neither email nor phone provided
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_get_student_by_id(client):
    """Test retrieving an existing student by student_id."""
    client.post("/students", json={
        "student_id": "STU_VIEW_01",
        "name": "Kavita Reddy",
        "date_of_birth": "2002-09-12",
        "phone": "+91-9876543210",
        "course": "Data Science"
    })

    response = client.get("/students/STU_VIEW_01")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kavita Reddy"
    assert data["course"] == "Data Science"


def test_get_student_not_found(client):
    """Test retrieving a non-existent student returns 404."""
    response = client.get("/students/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_and_filter_students(client):
    """Test listing and filtering students by course and search keyword."""
    client.post("/students", json={
        "student_id": "STU_A",
        "name": "Alice Wonderland",
        "date_of_birth": "2003-05-10",
        "email": "alice@example.com",
        "course": "Computer Science"
    })
    client.post("/students", json={
        "student_id": "STU_B",
        "name": "Bob Builder",
        "date_of_birth": "2005-08-20",
        "email": "bob@example.com",
        "course": "Mechanical"
    })

    # List all
    res_all = client.get("/students")
    assert res_all.status_code == 200
    assert res_all.json()["total"] == 2

    # Filter by course
    res_course = client.get("/students?course=Computer Science")
    assert res_course.status_code == 200
    assert res_course.json()["total"] == 1
    assert res_course.json()["students"][0]["name"] == "Alice Wonderland"

    # Filter by search
    res_search = client.get("/students?search=Builder")
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["students"][0]["student_id"] == "STU_B"


def test_update_student_full(client):
    """Test full update (PUT) of student details."""
    client.post("/students", json={
        "student_id": "STU_UPDATE_01",
        "name": "Original Name",
        "date_of_birth": "2002-01-01",
        "email": "orig@example.com",
        "course": "Physics"
    })

    update_payload = {
        "name": "Updated Name",
        "date_of_birth": "2002-01-01",
        "email": "updated@example.com",
        "course": "Mathematics",
        "phone": "+91-9999999999"
    }
    response = client.put("/students/STU_UPDATE_01", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["course"] == "Mathematics"
    assert data["email"] == "updated@example.com"


def test_update_student_partial(client):
    """Test partial update (PATCH) of student details."""
    client.post("/students", json={
        "student_id": "STU_PATCH_01",
        "name": "Jane Doe",
        "date_of_birth": "2003-03-03",
        "email": "jane@example.com",
        "course": "Biology"
    })

    # Partial update - only change course
    response = client.patch("/students/STU_PATCH_01", json={"course": "Biotechnology"})
    assert response.status_code == 200
    data = response.json()
    assert data["course"] == "Biotechnology"
    assert data["name"] == "Jane Doe"  # Untouched


def test_delete_student(client):
    """Test deleting an existing student record."""
    client.post("/students", json={
        "student_id": "STU_DEL_01",
        "name": "To Delete",
        "date_of_birth": "2001-01-01",
        "email": "delete.me@example.com"
    })

    # Delete
    del_res = client.delete("/students/STU_DEL_01")
    assert del_res.status_code == 200

    # Verify not found afterwards
    get_res = client.get("/students/STU_DEL_01")
    assert get_res.status_code == 404


def test_delete_non_existent_student(client):
    """Test deleting non-existent student returns 404."""
    response = client.delete("/students/DOES_NOT_EXIST")
    assert response.status_code == 404


def test_ai_query_endpoint(client):
    """Test the AI query endpoint returns grounded response."""
    # Seed a student
    client.post("/students", json={
        "student_id": "AI_STU_01",
        "name": "AI Learner",
        "date_of_birth": "2004-10-10",
        "email": "ai.learner@example.com",
        "course": "Artificial Intelligence"
    })

    query_payload = {"question": "How many students are enrolled in Artificial Intelligence?"}
    response = client.post("/ai/query", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "records_referenced" in data
    assert data["records_referenced"] >= 1
