from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserDocument(BaseModel):
    """
    Model representing user schema storage in MongoDB database.
    Documents are serialized to dictionaries before database insertion.
    """
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="Unique email address used for credential validation")
    password_hash: str = Field(..., description="Securely hashed bcrypt string representing user password")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Time profile was created")

    class Config:
        populate_by_name = True
        from_attributes = True
