from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserSignupSchema(BaseModel):
    """Schema for validating user registration requests."""
    name: str = Field(..., min_length=2, max_length=50, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

class UserLoginSchema(BaseModel):
    """Schema for validating user login requests."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User plain password")

class UserResponseSchema(BaseModel):
    """Schema for returning user details safely (excluding password)."""
    id: str = Field(..., alias="id", description="Unique user identifier (as string)")
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        # Allows Pydantic to read database dictionary objects or ODM attributes
        populate_by_name = True
        from_attributes = True

class TokenSchema(BaseModel):
    """Schema for returning JWT tokens to the client."""
    access_token: str
    token_type: str = "bearer"

class TokenDataSchema(BaseModel):
    """Internal schema for verifying decrypted token payloads."""
    email: Optional[str] = None
    user_id: Optional[str] = None
