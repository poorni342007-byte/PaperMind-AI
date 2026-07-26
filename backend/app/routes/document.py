from fastapi import APIRouter, UploadFile, File, Depends, status
from typing import List
from app.schemas import DocumentResponseSchema
from app.services.auth_service import AuthService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...), 
    current_user: dict = Depends(AuthService.get_current_user)
):
    """
    Upload a research paper PDF.
    Validates PDF format, saves to local server disk, and logs indexing details in MongoDB.
    """
    doc_record = await PDFService.save_and_initialize_document(file, current_user)
    return doc_record

@router.get("/list", response_model=List[DocumentResponseSchema])
async def list_documents(current_user: dict = Depends(AuthService.get_current_user)):
    """
    Retrieve metadata records of all research papers indexed by the active user.
    """
    docs = await PDFService.list_user_documents(current_user)
    return docs
