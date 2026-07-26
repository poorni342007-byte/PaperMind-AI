from pydantic import BaseModel, Field
from datetime import datetime

class DocumentResponseSchema(BaseModel):
    """Schema representing metadata structure returned for uploaded files."""
    id: str = Field(..., description="Database object ID of the file record")
    user_id: str = Field(..., description="Owner user ID")
    filename: str = Field(..., description="Original name of the PDF file")
    file_path: str = Field(..., description="Local folder storage path")
    uploaded_at: datetime = Field(..., description="Timestamp of upload")
    extracted_text_preview: str = Field(..., description="First 500 characters preview of extracted text")

    class Config:
        populate_by_name = True
        from_attributes = True
