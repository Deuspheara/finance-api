# Authentication & Multi-Tenancy API

## Overview

The authentication system provides JWT-based user authentication with complete multi-tenant data isolation. All protected endpoints require valid JWT tokens and enforce strict user data segregation.

## Authentication Endpoints

### User Login

Authenticate user credentials and receive JWT access token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email format or missing fields
- `401 Unauthorized`: Invalid credentials

### Get Current User

Retrieve authenticated user's profile information.

**Endpoint:** `GET /auth/me`

**Authentication:** Required (JWT token in Authorization header)

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication token

## JWT Token Usage

Include the JWT token in the Authorization header for all protected requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Properties:**
- **Algorithm:** HS256
- **Expiration:** 30 minutes (configurable)
- **Payload:** Contains user email and issued timestamp
- **Refresh:** Separate refresh token system (not implemented in current version)

## Multi-Tenant Architecture

### Data Isolation

The system enforces complete data isolation between users:

- **Database Level:** All queries filtered by user_id
- **API Level:** User ID validation on every request
- **Memory Level:** Conversation contexts isolated per user
- **Cache Level:** Redis keys prefixed by user ID

### User Context Enforcement

Every protected endpoint validates:

1. **Token Validity:** JWT signature and expiration
2. **User Existence:** User account is active
3. **Data Ownership:** Requesting user owns the data
4. **Permission Scope:** User can only access their own resources

### Cross-User Protection

- **Finance Tools:** Portfolio analysis isolated to user data
- **LLM Chat:** Conversation context per user only
- **Subscription Data:** Usage limits and billing per user
- **Privacy Data:** Consent and audit logs per user

## Data Models

### LoginRequest
```python
{
  "email": EmailStr,    # Valid email format required
  "password": str       # Plain text password
}
```

### TokenResponse
```python
{
  "access_token": str,    # JWT access token
  "token_type": str,      # Always "bearer"
  "expires_in": int       # Token validity in seconds
}
```

### UserResponse
```python
{
  "id": int,              # Unique user identifier
  "email": str,           # User email address
  "is_active": bool,      # Account status
  "created_at": datetime  # Account creation timestamp
}
```

### TokenData (Internal)
```python
{
  "email": str | None     # Email from JWT payload
}
```

## Security Features

### Password Security
- **Hashing:** bcrypt with automatic salt generation
- **Validation:** Minimum length and complexity requirements
- **Storage:** Secure hash storage only

### Token Security
- **Signing:** HMAC-SHA256 with server secret key
- **Expiration:** Short-lived tokens (30 minutes)
- **Revocation:** Not implemented (tokens valid until expiry)

### Request Security
- **Rate Limiting:** Configurable per-user and global limits
- **CORS:** Configured allowed origins
- **Input Validation:** Pydantic model validation on all inputs

## Multi-Tenant Benefits

- **Scalability:** Independent user scaling
- **Security:** Complete data isolation
- **Compliance:** GDPR-ready user data segregation
- **Performance:** User-specific caching and optimization

## Usage Examples

### Login Flow
```bash
# 1. Login to get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 2. Use token for authenticated requests
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Protected API Access
```bash
# All API endpoints require Bearer token
curl -X GET http://localhost:8000/api/v1/subscription \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Notes

- Tokens expire after 30 minutes
- Refresh token system not implemented in current version
- All user data is completely isolated
- Failed authentication attempts are logged
- Rate limiting applies to authentication endpoints