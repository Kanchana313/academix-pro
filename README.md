# 🎓 Academix Pro — Students Database CRUD Application (+ Optional AI Extension)

> **Python Backend Development Internship Project Assignment**  
> **Company:** EWB EDU TECH PVT. LTD. | **Project Type:** Individual Backend Development

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Architecture & Tech Stack](#-architecture--tech-stack)
4. [Project Directory Structure](#-project-directory-structure)
5. [Prerequisites & Requirements](#-prerequisites--requirements)
6. [Installation & Setup](#-installation--setup)
7. [Running the Application](#-running-the-application)
8. [API Documentation & Endpoints](#-api-documentation--endpoints)
9. [Sample Requests & cURL Examples](#-sample-requests--curl-examples)
10. [Optional AI Extension (Local Ollama)](#-optional-ai-extension-local-ollama)
11. [Running Automated Tests](#-running-automated-tests)
12. [Project Review Checklist](#-project-review-checklist)

---

## 🎯 Project Overview
This project is a backend application developed with **FastAPI** and **SQLite** to manage student records via standard Create, Read, Update, and Delete (**CRUD**) operations.

It also includes an **Optional Local AI Extension** integrating with **Ollama** (e.g., `llama3.2:1b`), allowing users to ask natural-language questions about students (such as *"How many students are there?"* or *"List students born after 2005"*). The backend fetches relevant records and provides them as factual context to the model, completely preventing raw SQL injection.

Additionally, a sleek **Interactive Web Dashboard** is provided directly at `http://127.0.0.1:8000/` for visual testing and demonstration alongside the interactive **Swagger UI** (`/docs`).

---

## ✨ Key Features
- **Create (POST /students)**: Adds new student records with unique `student_id` validation and contact verification (at least email or phone required).
- **Read (GET /students & GET /students/{student_id})**: Retrieve all students or filter by course, name/keyword search, birth date range, and pagination (`skip`/`limit`).
- **Update (PUT & PATCH /students/{student_id})**: Full profile updates or selective partial updates with validation.
- **Delete (DELETE /students/{student_id})**: Safely removes student records from persistent SQLite storage.
- **Input Validation & Error Handling**: Powered by Pydantic schemas (valid email validation, mandatory fields, descriptive HTTP 400, 404, 422 error responses).
- **Ollama AI Integration**: Safe context-grounded natural-language query engine. Has an automatic deterministic fallback if Ollama is offline.
- **Pre-populated Dummy Data**: Script provided to seed realistic dummy student records (no real personal info committed).
- **Automated Tests**: 100% test coverage for all endpoints with `pytest`.

---

## 🛠️ Architecture & Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: FastAPI (Asynchronous REST API)
- **Database & ORM**: SQLite + SQLAlchemy 2.0
- **Data Validation & Serialization**: Pydantic v2 + Pydantic-Settings
- **Server**: Uvicorn ASGI Server
- **HTTP & AI Client**: HTTPX
- **Testing**: Pytest + FastAPI TestClient
- **Frontend Dashboard**: Vanilla HTML5, Modern CSS (Glassmorphism), and JavaScript

---

## 📂 Project Directory Structure
```text
student-data/
├── app/
│   ├── __init__.py           # Application package initializer
│   ├── main.py               # FastAPI entrypoint, middleware, routes mounting
│   ├── config.py             # Pydantic environment configuration
│   ├── database.py           # SQLite engine, session maker, get_db dependency
│   ├── models.py             # SQLAlchemy ORM student model
│   ├── schemas.py            # Pydantic request/response schemas & validation
│   ├── crud.py               # Database queries (CRUD operations & filters)
│   ├── ai_service.py         # Ollama client & grounded query logic
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py       # CRUD endpoints (/students)
│   │   └── ai.py             # Natural language AI query endpoints (/ai)
│   └── static/               # Interactive Web Dashboard UI
│       ├── index.html        # Clean dashboard interface
│       ├── style.css         # Modern dark-mode styling
│       └── app.js            # Client-side API integration
├── tests/
│   ├── __init__.py
│   └── test_students.py      # Automated Pytest suite
├── .env.example              # Template environment variables
├── .gitignore                # Git exclusions (venv, db, cache, secrets)
├── requirements.txt          # Python dependencies
├── sample_data.py            # Dummy database seeding script
└── README.md                 # Complete documentation
```

---

## 📋 Prerequisites & Requirements
- **Python**: Version 3.10 or higher
- **Git**: For version control and GitHub submission
- **Ollama** *(Optional for AI challenge)*: Downloaded from [ollama.com](https://ollama.com)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd "student data"
```

### 2. Create and Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On Linux/macOS:
cp .env.example .env
```

### 5. Seed Sample Dummy Records (Optional but Recommended)
Populate the database with sample student profiles:
```bash
python sample_data.py
```
*Output: `Successfully seeded 8 dummy student records into SQLite database.`*

---

## 🖥️ Running the Application

Start the FastAPI application with Uvicorn:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

Once started, access the following in your web browser:
- **Interactive Web Dashboard**: `http://127.0.0.1:8000/`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Alternative ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **Health Check Endpoint**: `http://127.0.0.1:8000/health`

---

## 📡 API Documentation & Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **POST** | `/students` | Create a new student record | `201 Created` |
| **GET** | `/students` | List all students (with search, filter, pagination) | `200 OK` |
| **GET** | `/students/{student_id}` | Retrieve individual student profile by ID | `200 OK` / `404` |
| **PUT** | `/students/{student_id}` | Full update of existing student | `200 OK` / `404` / `422` |
| **PATCH** | `/students/{student_id}` | Partial update of student fields | `200 OK` / `404` / `422` |
| **DELETE** | `/students/{student_id}` | Remove a student from database | `200 OK` / `404` |
| **GET** | `/students/stats/summary` | Summary counts & course distribution | `200 OK` |
| **POST** | `/ai/query` | Ask natural language question with Ollama | `200 OK` |
| **GET** | `/ai/status` | Check local Ollama availability | `200 OK` |
| **GET** | `/health` | API operational health check | `200 OK` |

---

## 🧪 Sample Requests & cURL Examples

### 1. Create a Student (`POST /students`)
```bash
curl -X POST "http://127.0.0.1:8000/students" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "STU1010",
       "name": "Tanvi Joshi",
       "date_of_birth": "2004-03-22",
       "email": "tanvi.joshi@example.com",
       "phone": "+91-9876500000",
       "course": "Computer Science",
       "address": "25 Residency Road, Bengaluru",
       "enrollment_date": "2023-08-01"
     }'
```

### 2. List & Filter Students (`GET /students`)
- **List with Pagination:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students?skip=0&limit=10"
  ```
- **Filter by Course:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students?course=Computer%20Science"
  ```
- **Filter Students Born After a Date:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students?born_after=2004-01-01"
  ```

### 3. Retrieve Individual Student Profile (`GET /students/{student_id}`)
```bash
curl -X GET "http://127.0.0.1:8000/students/STU1001"
```

### 4. Partial Update (`PATCH /students/{student_id}`)
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU1001" \
     -H "Content-Type: application/json" \
     -d '{
       "course": "Artificial Intelligence & Data Science"
     }'
```

### 5. Delete a Student (`DELETE /students/{student_id}`)
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU1010"
```

---

## 🤖 Optional AI Extension (Local Ollama)

The application includes an optional extension to answer natural-language queries about your SQLite database using **Ollama**:

### How It Works:
1. User sends a natural language question (e.g., *"How many students are there?"* or *"List students born after 2005"*).
2. The backend **safely retrieves** relevant records using SQLAlchemy ORM (preventing any direct SQL execution).
3. The records are structured into factual context and passed to the local Ollama LLM (`llama3.2:1b`).
4. The model returns a human-readable response grounded strictly in the verified database facts.
5. If Ollama is offline, the backend features an **automatic grounded fallback** that answers directly from the retrieved database statistics, ensuring no system crashes.

### Running with Ollama:
1. Install Ollama and pull the model:
   ```bash
   ollama pull llama3.2:1b
   ```
2. Start the Ollama local service:
   ```bash
   ollama serve
   ```
3. Query via API or the Web Dashboard UI:
   ```bash
   curl -X POST "http://127.0.0.1:8000/ai/query" \
        -H "Content-Type: application/json" \
        -d '{"question": "How many students are enrolled in Computer Science?"}'
   ```

---

## 🧪 Running Automated Tests

Run the comprehensive pytest test suite:
```bash
pytest -v
```

All 12 unit and integration tests execute against an isolated in-memory SQLite database:
- ✅ Health check verification
- ✅ Student creation (Success & Schema validation)
- ✅ Duplicate ID prevention (HTTP 400)
- ✅ Missing contact info validation (HTTP 422)
- ✅ Single student retrieval & 404 handling
- ✅ List filtering & keyword search
- ✅ Full updates (PUT) & Partial updates (PATCH)
- ✅ Student deletion & subsequent 404 confirmation
- ✅ Grounded AI query handling

---

## ✅ Project Review Checklist
- [x] **All four CRUD operations work correctly**: POST, GET, PUT/PATCH, and DELETE fully implemented.
- [x] **SQLite data persists and can be retrieved accurately**: Data persists in `students.db`.
- [x] **Input validation and missing-record handling work properly**: Validated via Pydantic; proper HTTP status codes (`400`, `404`, `422`, `500`).
- [x] **Code is organized and README instructions are reproducible**: Modular clean architecture with virtual environment setup.
- [x] **Optional AI answers grounded in retrieved records**: Implemented with Ollama integration and safe context grounding.
- [x] **No hardcoded secrets or personal data**: Secure `.gitignore`, `.env.example`, and dummy sample data.

---

**Developed for EWB Edu Tech Pvt. Ltd. Internship Assessment**
