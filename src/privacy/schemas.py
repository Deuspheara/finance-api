from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

class ConsentRequest(BaseModel):
    user_id: UUID
    consent_type: str
    granted: bool

class ConsentData(BaseModel):
    id: UUID
    consent_type: str
    granted: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLogData(BaseModel):
    id: UUID
    action: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class DataExportResponse(BaseModel):
    user_id: UUID
    consents: List[ConsentData]
    audit_logs: List[AuditLogData]

    class Config:
        from_attributes = True