from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConsentRequest(BaseModel):
    user_id: UUID
    consent_type: str
    granted: bool


class ConsentData(BaseModel):
    id: UUID
    consent_type: str
    granted: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogData(BaseModel):
    id: UUID
    action: str
    details: dict[str, Any] | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class DataExportResponse(BaseModel):
    user_id: UUID
    consents: list[ConsentData]
    audit_logs: list[AuditLogData]

    model_config = ConfigDict(from_attributes=True)
