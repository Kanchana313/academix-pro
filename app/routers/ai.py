from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas
from app.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Extension (Ollama)"])

@router.post(
    "/query",
    response_model=schemas.AIQueryResponse,
    summary="Natural Language Query (Ollama + Grounded Records)",
    description=(
        "Answers natural-language questions about students (e.g., 'How many students are there?', 'List students born after 2005'). "
        "Fetches verified database records securely in backend code and grounds the response. "
        "Strictly protected against raw SQL injection."
    )
)
async def query_student_data_with_ai(
    payload: schemas.AIQueryRequest,
    db: Session = Depends(get_db)
):
    try:
        response = await ai_service.answer_question(
            db=db,
            question=payload.question,
            requested_model=payload.model
        )
        return schemas.AIQueryResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing AI query: {str(e)}"
        )


@router.get(
    "/status",
    summary="Check Ollama Connection Status",
    description="Check whether local Ollama service is reachable and view available local models."
)
async def get_ollama_status():
    return await ai_service.check_ollama_status()
