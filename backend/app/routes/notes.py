from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas import NotesRequestSchema, NotesResponseSchema
from app.services.auth_service import AuthService
from app.services.notes_service import NotesService

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/generate", response_model=NotesResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_notes(
    payload: NotesRequestSchema,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """
    Request simplified study notes generated from an uploaded PDF.
    Prompts Gemini to summarize sections, extract takeaways, 
    and construct glossaries, returning structured JSON datasets.
    """
    notes_record = await NotesService.generate_notes(
        document_id=payload.document_id,
        notes_type=payload.notes_type,
        current_user=current_user
    )
    return notes_record

@router.get("/history", response_model=List[NotesResponseSchema])
async def get_notes_history(current_user: dict = Depends(AuthService.get_current_user)):
    """
    Retrieve previously generated simplified study notes records.
    """
    history = await NotesService.get_notes_history(current_user)
    return history
