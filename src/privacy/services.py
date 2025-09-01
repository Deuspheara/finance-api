from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.metrics import gdpr_actions_total
from src.privacy.models import AuditLog, UserConsent


class GDPRService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_consent(self, user_id: UUID, consent_type: str, granted: bool):
        # Create consent record
        consent = UserConsent(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted
        )
        self.session.add(consent)
        await self.session.commit()
        await self.session.refresh(consent)

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="consent_recorded",
            details=AuditLog.encrypt_details({"consent_type": consent_type, "granted": granted})
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)

        # Increment metrics
        gdpr_actions_total.labels(action_type="record_consent").inc()

    async def export_user_data(self, user_id: UUID) -> dict:
        # Export consents
        consent_stmt = select(UserConsent).where(UserConsent.user_id == user_id)
        consent_result = await self.session.execute(consent_stmt)
        consents = consent_result.scalars().all()

        # Export audit logs
        audit_stmt = select(AuditLog).where(AuditLog.user_id == user_id)
        audit_result = await self.session.execute(audit_stmt)
        audits = audit_result.scalars().all()

        result = {
            "user_id": user_id,
            "consents": [
                {
                    "id": c.id,
                    "consent_type": c.consent_type,
                    "granted": c.granted,
                    "timestamp": c.timestamp.isoformat()
                } for c in consents
            ],
            "audit_logs": [
                {
                    "id": a.id,
                    "action": a.action,
                    "details": AuditLog.decrypt_details(a.details),
                    "timestamp": a.timestamp.isoformat()
                } for a in audits
            ]
        }

        # Increment metrics
        gdpr_actions_total.labels(action_type="export_data").inc()

        return result

    async def anonymize_user_data(self, user_id: UUID):
        # Delete consents
        consent_stmt = select(UserConsent).where(UserConsent.user_id == user_id)
        consent_result = await self.session.execute(consent_stmt)
        consents = consent_result.scalars().all()
        for consent in consents:
            await self.session.delete(consent)

        # Delete audit logs
        audit_stmt = select(AuditLog).where(AuditLog.user_id == user_id)
        audit_result = await self.session.execute(audit_stmt)
        audits = audit_result.scalars().all()
        for audit in audits:
            await self.session.delete(audit)

        await self.session.commit()

        # Increment metrics
        gdpr_actions_total.labels(action_type="anonymize_data").inc()

        # Log the anonymization (but since we're deleting, maybe log before or use a separate audit)
        # For simplicity, skip logging here as data is being deleted
