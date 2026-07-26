from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Any, Optional, Dict, Union

class SourceItemSchema(BaseModel):
    page: int
    chunk_id: int
    preview: str
    retrieval_score: float = 0.0
    reranker_score: float = 0.0

class ChatRequestSchema(BaseModel):
    """Schema for validating user Q&A queries against a PDF."""
    document_id: str = Field(..., description="Document ID to index context from")
    question: str = Field(..., min_length=2, max_length=500, description="User's query or question")
    debug: Optional[bool] = Field(default=False, description="Enable debug retrieval output")

class ChatResponseSchema(BaseModel):
    """Schema for returning conversation records."""
    id: Optional[str] = Field(default=None, description="Chat record primary key ID")
    user_id: Optional[str] = Field(default=None)
    document_id: str
    question: str
    answer: str
    sources: List[Union[SourceItemSchema, Dict[str, Any], str]] = Field(default=[], description="Source paragraph pages or chunks matched")
    grounded: bool = Field(default=True, description="Whether answer was supported by document evidence")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    debug: Optional[Dict[str, Any]] = Field(default=None, description="Debug search metadata")

    class Config:
        populate_by_name = True
        from_attributes = True
