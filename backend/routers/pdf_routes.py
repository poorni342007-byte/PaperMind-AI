import os
import shutil
import glob
from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from models import DocumentResponse, SummaryResponse
from database import documents_collection, chats_collection
from auth import get_current_user
from pdf_utils import extract_text_from_pdf
from rag_engine import index_document_file, index_document_text, generate_notes_summary

router = APIRouter(prefix="/pdf", tags=["PDF Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
async def upload_pdf(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )
    
    # Save the file locally
    file_path = os.path.join(UPLOAD_DIR, f"{current_user['_id']}_{datetime.utcnow().timestamp()}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Extract preview text
    extracted_text = extract_text_from_pdf(file_path)
    preview_length = min(len(extracted_text), 500)
    preview = extracted_text[:preview_length]
    
    # Create document metadata record
    doc_record = {
        "user_id": str(current_user["_id"]),
        "filename": file.filename,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow(),
        "extracted_text_preview": preview
    }
    
    # Insert in DB
    result = await documents_collection.insert_one(doc_record)
    doc_id_str = str(result.inserted_id)
    
    # Index document with page-aware structured chunking, vector store, and reranker prep
    index_document_file(doc_id_str, file_path)
    
    return DocumentResponse(
        id=doc_id_str,
        user_id=doc_record["user_id"],
        filename=doc_record["filename"],
        uploaded_at=doc_record["uploaded_at"],
        extracted_text_preview=doc_record["extracted_text_preview"]
    )

@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List all documents uploaded by the authenticated user."""
    cursor = documents_collection.find({"user_id": str(current_user["_id"])})
    docs = []
    async for doc in cursor:
        docs.append(DocumentResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            filename=doc["filename"],
            uploaded_at=doc["uploaded_at"],
            extracted_text_preview=doc["extracted_text_preview"]
        ))
    return docs

@router.get("/{document_id}/summary", response_model=SummaryResponse)
async def get_summary(document_id: str, current_user: dict = Depends(get_current_user)):
    """Generate simplified notes/summary for a research paper."""
    # Find document
    try:
        doc = await documents_collection.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format."
        )
        
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    
    summary_data = generate_notes_summary(document_id, doc["filename"])
    return SummaryResponse(
        document_id=summary_data["document_id"],
        summary=summary_data["summary"],
        notes=summary_data["notes"]
    )

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document, its index files, and all associated chat history."""
    try:
        # 1. Verify document exists and belongs to the current user
        doc = await documents_collection.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format."
        )
        
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied."
        )
        
    # 2. Delete physical PDF file from uploads
    file_path = doc.get("file_path")
    if not file_path:
        pattern = os.path.join(UPLOAD_DIR, f"{current_user['_id']}_*_{doc['filename']}")
        matches = glob.glob(pattern)
        if matches:
            file_path = matches[0]
            
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"[Delete] Removed file: {file_path}")
        except Exception as e:
            print(f"[Delete] Error removing file {file_path}: {e}")
            
    # 3. Delete index files from indices/
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_dir = os.path.join(backend_dir, "indices")
    
    index_path = os.path.join(index_dir, f"{document_id}.index")
    metadata_path = os.path.join(index_dir, f"{document_id}_metadata.json")
    chunks_path = os.path.join(index_dir, f"{document_id}_chunks.json")
    text_path = os.path.join(index_dir, f"{document_id}.txt")
    
    for path in [index_path, metadata_path, chunks_path, text_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"[Delete] Removed index file: {path}")
            except Exception as e:
                print(f"[Delete] Error removing index file {path}: {e}")
                
    # 4. Clean up MongoDB records
    await documents_collection.delete_one({"_id": ObjectId(document_id)})
    chats_deleted = await chats_collection.delete_many({"document_id": document_id})
    print(f"[Delete] Deleted {chats_deleted.deleted_count} chat records from DB")
    
    return {"message": "Document and all associated data successfully deleted"}
