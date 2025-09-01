from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import ConfigDict
from src.core.encryption import EncryptionService
from uuid import UUID, uuid4

class UserConsent(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    consent_type: str
    granted: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    action: str
    details: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def encrypt_details(details_dict: Optional[Dict[str, Any]]) -> Optional[str]:
        if details_dict is None:
            return None
        encryption_service = EncryptionService()
        return encryption_service.encrypt_data(details_dict)

    @staticmethod
    def decrypt_details(encrypted_details: Optional[str]) -> Optional[Dict[str, Any]]:
        if encrypted_details is None:
            return None
        encryption_service = EncryptionService()
        return encryption_service.decrypt_data(encrypted_details)