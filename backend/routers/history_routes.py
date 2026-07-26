from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from models import ChatResponse
from database import chats_collection, documents_collection
from auth import get_current_user

router = APIRouter(prefix="/history", tags=["Chat History"])

@router.get("/chats/{document_id}", response_model=List[ChatResponse])
async def get_document_chat_history(document_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch previous Q&A chat history for a specific document."""
    try:
        # Check if the document belongs to this user
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
        
    cursor = chats_collection.find({
        "user_id": str(current_user["_id"]),
        "document_id": document_id
    }).sort("created_at", 1)  # Sort chronological (oldest first)
    
    chat_history = []
    async for chat in cursor:
        chat_history.append(ChatResponse(
            id=str(chat["_id"]),
            user_id=chat["user_id"],
            document_id=chat["document_id"],
            question=chat["question"],
            answer=chat["answer"],
            sources=chat["sources"],
            created_at=chat["created_at"]
        ))
    return chat_history

@router.get("/all", response_model=List[ChatResponse])
async def get_all_chat_history(current_user: dict = Depends(get_current_user)):
    """Fetch all Q&A chat histories for the authenticated user."""
    cursor = chats_collection.find({
        "user_id": str(current_user["_id"])
    }).sort("created_at", -1)  # Sort newest first
    
    chat_history = []
    async for chat in cursor:
        chat_history.append(ChatResponse(
            id=str(chat["_id"]),
            user_id=chat["user_id"],
            document_id=chat["document_id"],
            question=chat["question"],
            answer=chat["answer"],
            sources=chat["sources"],
            created_at=chat["created_at"]
        ))
    return chat_history
