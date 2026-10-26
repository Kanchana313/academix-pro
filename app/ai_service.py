import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app import models, crud

class AIService:
    """
    Ollama AI Service that grounds natural language responses in database records.
    Secured against SQL injection by using strictly typed backend ORM queries
    and passing only retrieved record contexts to the LLM.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.default_model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_ollama_status(self) -> Dict[str, Any]:
        """Check if local Ollama server is running and which models are installed."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models_list = [m.get("name") for m in data.get("models", [])]
                    return {
                        "available": True,
                        "base_url": self.base_url,
                        "models": models_list,
                        "default_model": self.default_model,
                    }
        except Exception as e:
            return {
                "available": False,
                "base_url": self.base_url,
                "error": str(e),
                "default_model": self.default_model,
                "note": "Ollama is not running locally. Fallback rule-based grounded answering is active."
            }
        return {"available": False, "base_url": self.base_url}

    def fetch_relevant_records(self, db: Session, question: str) -> Dict[str, Any]:
        """
        Backend code fetches relevant database records safely based on the question.
        Never executes raw SQL from the user or model.
        """
        q_lower = question.lower()
        stats = crud.get_stats(db)
        
        # 1. Year matching (e.g. 'born after 2005', 'born in 2003')
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', q_lower)
        target_year = int(year_match.group(1)) if year_match else None

        # 2. Check for course mentions
        all_courses = db.query(models.Student.course).distinct().all()
        matched_course = None
        for (c,) in all_courses:
            if c and c.lower() in q_lower:
                matched_course = c
                break

        # 3. Build query based on detected intents
        query = db.query(models.Student)

        if "after" in q_lower and target_year:
            # Born after Dec 31 of that year
            cutoff_date = date(target_year, 12, 31)
            query = query.filter(models.Student.date_of_birth > cutoff_date)
        elif "before" in q_lower and target_year:
            # Born before Jan 1 of that year
            cutoff_date = date(target_year, 1, 1)
            query = query.filter(models.Student.date_of_birth < cutoff_date)
        elif target_year:
            # Born in specific year
            query = query.filter(
                func.strftime('%Y', models.Student.date_of_birth) == str(target_year)
            )

        if matched_course:
            query = query.filter(models.Student.course.ilike(f"%{matched_course}%"))

        # If question is asking about specific student name or id
        name_id_candidates = re.findall(r'[A-Za-z0-9_-]{3,}', question)
        name_matched_students = []
        for word in name_id_candidates:
            if word.lower() not in ["how", "many", "students", "there", "list", "show", "who", "what", "born", "after", "before", "from", "with", "course"]:
                found = db.query(models.Student).filter(
                    (models.Student.name.ilike(f"%{word}%")) |
                    (models.Student.student_id.ilike(f"%{word}%"))
                ).all()
                if found:
                    name_matched_students.extend(found)

        if name_matched_students:
            students = list({s.id: s for s in name_matched_students}.values())
        else:
            students = query.order_by(models.Student.id.asc()).limit(50).all()

        student_data = [
            {
                "student_id": s.student_id,
                "name": s.name,
                "date_of_birth": str(s.date_of_birth),
                "course": s.course or "Not specified",
                "email": s.email or "N/A",
                "phone": s.phone or "N/A",
                "enrollment_date": str(s.enrollment_date) if s.enrollment_date else "N/A"
            }
            for s in students
        ]

        return {
            "total_in_system": stats["total_students"],
            "courses_summary": stats["course_distribution"],
            "matched_records": student_data,
            "matched_count": len(student_data),
        }

    async def answer_question(
        self,
        db: Session,
        question: str,
        requested_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer question by:
        1. Fetching relevant records safely in backend code.
        2. Supplying records as factual context to Ollama LLM.
        3. If Ollama is offline, gracefully return grounded response generated directly from records.
        """
        model = requested_model or self.default_model
        context_data = self.fetch_relevant_records(db, question)
        
        # Prepare context prompt
        records_text = "\n".join([
            f"- ID: {r['student_id']} | Name: {r['name']} | DOB: {r['date_of_birth']} | Course: {r['course']} | Email: {r['email']} | Phone: {r['phone']}"
            for r in context_data["matched_records"]
        ])

        system_prompt = (
            "You are an AI assistant for a Student Database Management System. "
            "Your job is to answer questions strictly using the verified database records provided below. "
            "Never invent or extrapolate data. If the answer cannot be found in the records, state that clearly. "
            "Do not execute SQL or output raw SQL queries."
        )

        user_prompt = (
            f"Database Summary:\n"
            f"- Total students registered: {context_data['total_in_system']}\n"
            f"- Course Distribution: {context_data['courses_summary']}\n\n"
            f"Relevant Student Records ({context_data['matched_count']} records retrieved):\n"
            f"{records_text if records_text else 'No matching individual records found.'}\n\n"
            f"User Question: {question}\n\n"
            f"Please provide a clear, concise, and helpful answer grounded in the database records above:"
        )

        # Attempt to call Ollama
        try:
            payload = {
                "model": model,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    ollama_data = res.json()
                    answer = ollama_data.get("response", "").strip()
                    if answer:
                        return {
                            "question": question,
                            "answer": answer,
                            "records_referenced": context_data["matched_count"],
                            "matched_records_preview": context_data["matched_records"][:10],
                            "source": "ollama",
                            "model_used": model
                        }
        except Exception:
            # Ollama is unreachable or errored; use deterministic grounded fallback
            pass

        # Grounded backend fallback response
        fallback_answer = self._generate_grounded_fallback(question, context_data)
        return {
            "question": question,
            "answer": fallback_answer,
            "records_referenced": context_data["matched_count"],
            "matched_records_preview": context_data["matched_records"][:10],
            "source": "backend_grounded_fallback",
            "model_used": None
        }

    def _generate_grounded_fallback(self, question: str, context: Dict[str, Any]) -> str:
        """Deterministic, grounded natural language answer generated when Ollama is offline."""
        q_lower = question.lower()
        total = context["total_in_system"]
        matched_records = context["matched_records"]
        matched_count = context["matched_count"]

        if "how many students" in q_lower or "total students" in q_lower or "count" in q_lower:
            if matched_count < total and matched_count > 0:
                return (
                    f"There are currently {total} total students in the database. "
                    f"Based on your criteria, {matched_count} matching student(s) were found."
                )
            return f"There are currently a total of {total} student(s) registered in the database."

        if "course" in q_lower and ("list" in q_lower or "distribution" in q_lower or "what" in q_lower):
            courses_str = ", ".join([f"{k}: {v}" for k, v in context["courses_summary"].items()])
            return f"Course distribution across enrolled students: {courses_str}."

        if matched_records:
            student_bullets = "\n".join([
                f"• {s['name']} (ID: {s['student_id']}) - Born: {s['date_of_birth']}, Course: {s['course']}"
                for s in matched_records[:15]
            ])
            more_note = f"\n(and {len(matched_records) - 15} more)" if len(matched_records) > 15 else ""
            return (
                f"Found {matched_count} matching record(s) in the database:\n"
                f"{student_bullets}{more_note}"
            )

        return (
            f"No students matching your question were found in the database. "
            f"Total students registered: {total}."
        )

ai_service = AIService()
