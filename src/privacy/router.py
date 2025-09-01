from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4

from src.privacy.services import GDPRService
from src.privacy.schemas import ConsentRequest, DataExportResponse
from src.privacy.dependencies import get_gdpr_service
from src.auth.dependencies import get_current_active_user
from src.users.models import User
from src.privacy.tasks import generate_user_data_export

router = APIRouter()

@router.post("/consent")
async def record_consent(
    consent_request: ConsentRequest,
    current_user: User = Depends(get_current_active_user),
    gdpr_service: GDPRService = Depends(get_gdpr_service)
):
    # Ensure user can only record consent for themselves
    if consent_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot record consent for another user")
    
    await gdpr_service.record_consent(
        user_id=consent_request.user_id,
        consent_type=consent_request.consent_type,
        granted=consent_request.granted
    )
    return {"message": "Consent recorded successfully"}

@router.post("/export")
async def request_data_export(
    current_user: User = Depends(get_current_active_user)
):
    """Request GDPR data export - enqueues background task."""
    export_id = str(uuid4())

    # Enqueue the background export task
    task = generate_user_data_export.delay(current_user.id, export_id)

    return {
        "message": "Data export requested",
        "export_id": export_id,
        "task_id": task.id,
        "status": "processing"
    }

@router.delete("/anonymize")
async def anonymize_data(
    current_user: User = Depends(get_current_active_user),
    gdpr_service: GDPRService = Depends(get_gdpr_service)
):
    await gdpr_service.anonymize_user_data(current_user.id)
    return {"message": "User data anonymized successfully"}