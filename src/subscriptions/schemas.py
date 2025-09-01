from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    tier: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None

    class Config:
        from_attributes = True

class UsageLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    feature_name: str
    timestamp: datetime

    class Config:
        from_attributes = True