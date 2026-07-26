from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson import ObjectId
from models import ChatRequest, ChatResponse, QuizResponse, QuizQuestion
from database import documents_collection, chats_collection
from auth import get_current_user
from app.services.rag_service import RAGService
from rag_engine import generate_quiz_questions

router = APIRouter(prefix="/chat", tags=["PDF Q&A & Quiz"])

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Submit a research question about a PDF.
    Executes two-stage RAG (FAISS Top 10 + Cross-Encoder Top 4 + Local Ollama),
    and saves conversation details in MongoDB chats collection.
    """
    # Verify document exists and belongs to this user
    try:
        doc = await documents_collection.find_one({
            "_id": ObjectId(request.document_id),
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

    doc_filename = doc.get("filename", "Uploaded Document")

    # Process query using two-stage RAG engine
    rag_result = await RAGService.process_query(
        document_id=request.document_id,
        question=request.question,
        document_name=doc_filename,
        debug_mode=request.debug
    )
    
    # Save chat record in DB
    chat_record = {
        "user_id": str(current_user["_id"]),
        "document_id": request.document_id,
        "question": request.question,
        "answer": rag_result["answer"],
        "sources": rag_result.get("sources", []),
        "grounded": rag_result.get("grounded", True),
        "created_at": datetime.utcnow()
    }
    
    result = await chats_collection.insert_one(chat_record)
    
    return ChatResponse(
        id=str(result.inserted_id),
        user_id=chat_record["user_id"],
        document_id=chat_record["document_id"],
        question=chat_record["question"],
        answer=chat_record["answer"],
        sources=chat_record["sources"],
        grounded=chat_record["grounded"],
        created_at=chat_record["created_at"],
        debug=rag_result.get("debug")
    )

@router.get("/{document_id}/quiz", response_model=QuizResponse)
async def get_quiz(document_id: str, current_user: dict = Depends(get_current_user)):
    """Generate multiple-choice quiz questions based on the paper's contents."""
    # Verify document
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
        
    quiz_questions = generate_quiz_questions(document_id)
    questions_list = [QuizQuestion(**q) for q in quiz_questions]
    
    return QuizResponse(
        document_id=document_id,
        quiz=questions_list
    )
