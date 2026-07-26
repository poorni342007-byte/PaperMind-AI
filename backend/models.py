from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict, Union
from datetime import datetime

# --- Authentication Models ---

class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None


# --- Document Models ---

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    uploaded_at: datetime
    extracted_text_preview: str

    class Config:
        from_attributes = True


# --- Chat & History Models ---

class SourceItem(BaseModel):
    page: int
    chunk_id: int
    preview: str
    retrieval_score: float = 0.0
    reranker_score: float = 0.0

class ChatRequest(BaseModel):
    document_id: str
    question: str
    debug: Optional[bool] = False

class ChatResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    document_id: str
    question: str
    answer: str
    sources: List[Union[SourceItem, Dict[str, Any], str]] = []
    grounded: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    debug: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    document_id: str
    summary: str
    notes: List[str]

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str
    session: Optional[str] = "Session 1: Fundamentals & Core Concepts"

class QuizResponse(BaseModel):
    document_id: str
    quiz: List[QuizQuestion]

