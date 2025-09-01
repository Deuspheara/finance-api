from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.core.encryption import EncryptionService


class UserConsent(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    consent_type: str
    granted: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    action: str
    details: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def encrypt_details(details_dict: dict[str, Any] | None) -> str | None:
        if details_dict is None:
            return None
        encryption_service = EncryptionService()
        return encryption_service.encrypt_data(details_dict)

    @staticmethod
    def decrypt_details(encrypted_details: str | None) -> dict[str, Any] | None:
        if encrypted_details is None:
            return None
        encryption_service = EncryptionService()
        return encryption_service.decrypt_data(encrypted_details)
