from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.users.models import User


class Subscription(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    tier: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    stripe_customer_id: str | None = None
    user: Optional["User"] = Relationship(back_populates="subscriptions")


class UsageLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    feature_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
