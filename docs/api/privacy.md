# Privacy & GDPR API

## Overview

The privacy API provides GDPR compliance features including consent management, data export, and data anonymization. All endpoints require authentication and enforce user isolation.

## Endpoints

### Record Consent

Record or update user consent for data processing.

**Endpoint:** `POST /api/v1/privacy/consent`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "consent_type": "data_processing",
  "granted": true
}
```

**Response:**
```json
{
  "message": "Consent recorded successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid consent data
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Attempting to record consent for another user

### Request Data Export

Initiate a GDPR data export request (processed asynchronously).

**Endpoint:** `POST /api/v1/privacy/export`

**Authentication:** Required (JWT token)

**Response:**
```json
{
  "message": "Data export requested",
  "export_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery-task-id-123",
  "status": "processing"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication

### Anonymize Data

Permanently anonymize user data (GDPR right to erasure).

**Endpoint:** `DELETE /api/v1/privacy/anonymize`

**Authentication:** Required (JWT token)

**Response:**
```json
{
  "message": "User data anonymized successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication

## Data Export Process

Data exports are processed asynchronously using Celery:

1. **Request Submission:** User requests data export
2. **Background Processing:** Celery task collects all user data
3. **Data Compilation:** Includes consents, audit logs, usage data
4. **Export Generation:** Creates comprehensive data package
5. **Notification:** User notified when export is ready

## Consent Types

Supported consent types:

- `data_processing`: General data processing consent
- `marketing`: Marketing communications consent
- `analytics`: Analytics and tracking consent
- `third_party`: Third-party data sharing consent

## Data Anonymization

Anonymization process:

- **User Data:** Personal information replaced with anonymized identifiers
- **Conversations:** LLM chat history anonymized or deleted
- **Usage Logs:** Feature usage data anonymized
- **Audit Trail:** Anonymization action logged for compliance

## Data Models

### ConsentRequest
```python
{
  "user_id": UUID,       # Must match authenticated user ID
  "consent_type": str,   # Type of consent being recorded
  "granted": bool        # True for granted, False for revoked
}
```

### DataExportResponse
```python
{
  "user_id": UUID,
  "consents": List[ConsentData],
  "audit_logs": List[AuditLogData]
}
```

### ConsentData
```python
{
  "id": UUID,
  "consent_type": str,
  "granted": bool,
  "timestamp": datetime
}
```

### AuditLogData
```python
{
  "id": UUID,
  "action": str,
  "details": Dict[str, Any],  # Optional action details
  "timestamp": datetime
}
```

## GDPR Compliance Features

- **Right to Access:** Data export functionality
- **Right to Erasure:** Data anonymization endpoint
- **Consent Management:** Granular consent tracking
- **Audit Logging:** Complete action history
- **Data Portability:** Structured data export format

## Security Considerations

- **User Isolation:** Only users can access their own data
- **Audit Trail:** All privacy actions are logged
- **Data Encryption:** Sensitive data encrypted at rest
- **Access Control:** Strict authentication requirements

## Notes

- Data exports are processed in the background to avoid timeouts
- Anonymization is irreversible - use with caution
- All privacy actions are logged for compliance purposes
- Consent can be granted or revoked at any time
- Data retention follows GDPR requirements (configurable)