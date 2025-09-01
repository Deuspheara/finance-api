from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
