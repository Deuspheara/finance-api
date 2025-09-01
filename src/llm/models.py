from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ConversationLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    message: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
