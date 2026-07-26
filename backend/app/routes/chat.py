from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas import ChatRequestSchema, ChatResponseSchema
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/ask", response_model=ChatResponseSchema, status_code=status.HTTP_200_OK)
async def ask_question(
    payload: ChatRequestSchema,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """
    Submit a research question about an uploaded PDF document.
    Embeds the question, retrieves matching semantic segments via FAISS L2 search,
    and calls Google Gemini to return a simplified answer containing the sources.
    """
    chat_record = await ChatService.ask_question(
        document_id=payload.document_id,
        question=payload.question,
        current_user=current_user
    )
    return chat_record

@router.get("/history", response_model=List[ChatResponseSchema])
async def get_chat_history(current_user: dict = Depends(AuthService.get_current_user)):
    """
    Retrieve past Q&A conversation items queried by the active user.
    """
    history = await ChatService.get_chat_history(current_user)
    return history
