from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict

class NotesRequestSchema(BaseModel):
    """Schema for requesting simplified notes generation."""
    document_id: str = Field(..., description="Document ID to simplify")
    notes_type: str = Field(
        default="Simple",
        description="Complexity target: Simple, Intermediate, or Exam Revision"
    )

class ConceptSchema(BaseModel):
    """Key concept sub-object format."""
    concept_name: str = Field(..., description="Term name")
    definition: str = Field(..., description="Clear explanation")

class NotesResponseSchema(BaseModel):
    """Schema for returning generated study workspace notes."""
    id: str = Field(..., description="Unique record identifier")
    user_id: str
    document_id: str
    notes_type: str
    summary: str = Field(..., description="Comprehensive high-level summary of the paper")
    key_takeaways: List[str] = Field(..., description="Bullet list of main takeaways")
    important_concepts: List[ConceptSchema] = Field(..., description="Important terms glossary mapping")
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
