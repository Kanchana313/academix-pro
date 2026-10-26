import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import engine, Base
from app.routers import students, ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event to create database tables on startup."""
    # Create SQLite tables if they do not exist yet
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 🎓 Academix Pro — Students Database CRUD Application (+ Optional Ollama AI Extension)
### EWB Edu Tech Pvt. Ltd. Internship Assignment

This production-ready REST API provides full management of student profiles with persistent SQLite storage:
- **Create**: Add new student records (`POST /students`)
- **Read**: List & filter students (`GET /students`) and retrieve individual profiles (`GET /students/{student_id}`)
- **Update**: Full (`PUT /students/{student_id}`) or partial (`PATCH /students/{student_id}`) modifications
- **Delete**: Remove student records (`DELETE /students/{student_id}`)
- **AI Extension (Ollama)**: Query student data using natural language (`POST /ai/query`) with safe context grounding.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(students.router)
app.include_router(ai.router)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Dashboard"], summary="Student Management Dashboard UI")
def serve_dashboard():
    """Serves the interactive frontend web dashboard."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "message": "Welcome to Academix Pro - Student Database CRUD API",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "students": "/students",
            "ai_query": "/ai/query",
            "ai_status": "/ai/status"
        }
    })

@app.get("/health", tags=["System"], summary="Health Check")
def health_check():
    """Returns application health and operational status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "SQLite (Connected)",
        "docs_url": "/docs"
    }
