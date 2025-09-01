from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True