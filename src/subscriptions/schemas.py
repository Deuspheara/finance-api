from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    tier: str
    created_at: datetime
    updated_at: datetime | None = None
    stripe_customer_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UsageLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    feature_name: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
