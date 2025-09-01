from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from src.subscriptions.models import Subscription

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False

class User(UserBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    subscriptions: list["Subscription"] = Relationship(back_populates="user")