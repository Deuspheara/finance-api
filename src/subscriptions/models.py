from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from src.users.models import User

class Subscription(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    tier: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    user: Optional["User"] = Relationship(back_populates="subscriptions")

class UsageLog(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    feature_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)