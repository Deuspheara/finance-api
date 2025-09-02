from uuid import UUID

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.privacy.models import AuditLog, UserConsent
from src.privacy.services import GDPRService


@pytest.mark.asyncio
async def test_consent_recording(client: AsyncClient, test_session: AsyncSession):
    """Test recording user consent creates proper records"""
    # Create user and login
    user_data = {"email": "consent@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = UUID(response.json()["id"])

    # Login to get token
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record consent
    consent_data = {
        "user_id": str(user_id),
        "consent_type": "marketing_emails",
        "granted": True,
    }

    response = await client.post("/privacy/consent", json=consent_data, headers=headers)
    assert response.status_code == 200

    # Verify consent was recorded
    GDPRService(test_session)
    # Check database directly since export might be async
    from sqlalchemy import select

    result = await test_session.execute(
        select(UserConsent).where(UserConsent.user_id == user_id)
    )
    consents = result.scalars().all()

    assert len(consents) == 1
    assert consents[0].consent_type == "marketing_emails"
    assert consents[0].granted is True

    # Check audit log was created
    audit_result = await test_session.execute(
        select(AuditLog).where(AuditLog.user_id == user_id)
    )
    audits = audit_result.scalars().all()

    assert len(audits) == 1
    assert audits[0].action == "consent_recorded"


@pytest.mark.asyncio
async def test_data_export_functionality(
    client: AsyncClient, test_session: AsyncSession
):
    """Test data export retrieves user data correctly"""
    # Create user and login
    user_data = {"email": "export@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = UUID(response.json()["id"])

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record some consents
    gdpr_service = GDPRService(test_session)
    await gdpr_service.record_consent(user_id, "marketing_emails", True)
    await gdpr_service.record_consent(user_id, "data_processing", False)

    # Test export endpoint
    response = await client.post("/privacy/export", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "export_id" in data
    assert "task_id" in data
    assert data["status"] == "processing"

    # Test direct service export
    export_data = await gdpr_service.export_user_data(user_id)

    assert export_data["user_id"] == user_id
    assert len(export_data["consents"]) == 2
    assert len(export_data["audit_logs"]) == 2  # One for each consent

    consent_types = [c["consent_type"] for c in export_data["consents"]]
    assert "marketing_emails" in consent_types
    assert "data_processing" in consent_types


@pytest.mark.asyncio
async def test_anonymization_on_user_deletion(
    client: AsyncClient, test_session: AsyncSession
):
    """Test that user data is anonymized when user requests deletion"""
    # Create user and login
    user_data = {"email": "anonymize@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = UUID(response.json()["id"])

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record some data
    gdpr_service = GDPRService(test_session)
    await gdpr_service.record_consent(user_id, "test_consent", True)

    # Verify data exists
    from sqlalchemy import select

    result = await test_session.execute(
        select(UserConsent).where(UserConsent.user_id == user_id)
    )
    consents_before = result.scalars().all()
    assert len(consents_before) == 1

    audit_result = await test_session.execute(
        select(AuditLog).where(AuditLog.user_id == user_id)
    )
    audits_before = audit_result.scalars().all()
    assert len(audits_before) == 1

    # Anonymize data
    response = await client.delete("/privacy/anonymize", headers=headers)
    assert response.status_code == 200

    # Verify data was deleted
    result = await test_session.execute(
        select(UserConsent).where(UserConsent.user_id == user_id)
    )
    consents_after = result.scalars().all()
    assert len(consents_after) == 0

    audit_result = await test_session.execute(
        select(AuditLog).where(AuditLog.user_id == user_id)
    )
    audits_after = audit_result.scalars().all()
    assert len(audits_after) == 0


@pytest.mark.asyncio
async def test_consent_validation(client: AsyncClient):
    """Test that users can only record consent for themselves"""
    # Create two users
    user1_data = {"email": "user1@example.com", "password": "testpassword123"}
    user2_data = {"email": "user2@example.com", "password": "testpassword123"}

    response1 = await client.post("/users/", json=user1_data)
    response1.json()["id"]

    response2 = await client.post("/users/", json=user2_data)
    user2_id = response2.json()["id"]

    # Login as user1
    login_response = await client.post("/auth/login", json=user1_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to record consent for user2
    consent_data = {
        "user_id": str(user2_id),
        "consent_type": "marketing_emails",
        "granted": True,
    }

    response = await client.post("/privacy/consent", json=consent_data, headers=headers)
    assert response.status_code == 403
