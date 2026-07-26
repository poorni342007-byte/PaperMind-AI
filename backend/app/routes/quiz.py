from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas import QuizRequestSchema, QuizResponseSchema
from app.services.auth_service import AuthService
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/generate", response_model=QuizResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    payload: QuizRequestSchema,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """
    Request multiple-choice study questions generated from an uploaded PDF.
    Prompts Gemini to design questions, distractors options, correct answers,
    and feedback explanation strings, returning structured JSON datasets.
    """
    quiz_record = await QuizService.generate_quiz(
        document_id=payload.document_id,
        quiz_type=payload.quiz_type,
        difficulty=payload.difficulty,
        current_user=current_user
    )
    return quiz_record

@router.get("/history", response_model=List[QuizResponseSchema])
async def get_quiz_history(current_user: dict = Depends(AuthService.get_current_user)):
    """
    Retrieve previously generated multiple-choice study quizzes.
    """
    history = await QuizService.get_quiz_history(current_user)
    return history
