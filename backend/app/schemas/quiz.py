from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class QuizRequestSchema(BaseModel):
    """Schema for requesting a dynamically generated quiz."""
    document_id: str = Field(..., description="Document ID to quiz the user on")
    quiz_type: str = Field(
        default="MCQs",
        description="Format: MCQs, True/False, or Short Answer"
    )
    difficulty: str = Field(
        default="Medium",
        description="Difficulty level: Easy, Medium, or Hard"
    )

class QuizQuestionSchema(BaseModel):
    """MCQ individual question format."""
    question: str = Field(..., description="The quiz question text")
    options: List[str] = Field(default=[], description="List of possible options (for MCQs)")
    correct_option_index: int = Field(default=0, description="0-indexed location of correct answer")
    explanation: str = Field(..., description="Educator feedback explaining why this option is correct")

class QuizResponseSchema(BaseModel):
    """Schema for returning full quiz list content."""
    id: str = Field(..., description="Quiz record primary ID")
    user_id: str
    document_id: str
    quiz_type: str
    difficulty: str
    questions: List[QuizQuestionSchema]
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

class QuizAttemptSubmitSchema(BaseModel):
    """Schema for submitting student answers to log final scores."""
    quiz_id: str = Field(..., description="ID of the quiz record")
    score: int = Field(..., ge=0, description="Calculated student score")
