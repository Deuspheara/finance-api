# API Usage Examples

This document provides comprehensive curl examples for all API endpoints with request/response samples.

## Authentication

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Subscription Management

### Get Subscription
```bash
curl -X GET http://localhost:8000/api/v1/subscription \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "tier": "free",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "stripe_customer_id": "cus_1234567890"
}
```

### Get Usage Logs
```bash
curl -X GET http://localhost:8000/api/v1/usage \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "feature_name": "portfolio",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "feature_name": "llm_requests",
    "timestamp": "2024-01-01T01:00:00Z"
  }
]
```

## Finance Tools

### Analyze Portfolio
```bash
curl -X POST http://localhost:8000/api/v1/finance/portfolio/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {
        "symbol": "AAPL",
        "weight": 0.6,
        "price": 150.0
      },
      {
        "symbol": "GOOGL",
        "weight": 0.4,
        "price": 2500.0
      }
    ]
  }'
```

**Response:**
```json
{
  "analysis": {
    "expected_return": 0.085,
    "volatility": 0.15,
    "sharpe_ratio": 0.567
  }
}
```

## LLM Chat

### Chat with LLM
```bash
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "message": "What are the best investment strategies for beginners?"
  }'
```

**Response:**
```json
{
  "response": "For beginners, I recommend starting with a diversified portfolio through index funds or ETFs. Focus on long-term investing rather than trying to time the market. Consider your risk tolerance and investment timeline before making decisions."
}
```

## Privacy & GDPR

### Record Consent
```bash
curl -X POST http://localhost:8000/api/v1/privacy/consent \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "consent_type": "data_processing",
    "granted": true
  }'
```

**Response:**
```json
{
  "message": "Consent recorded successfully"
}
```

### Request Data Export
```bash
curl -X POST http://localhost:8000/api/v1/privacy/export \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "message": "Data export requested",
  "export_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery-task-id-123",
  "status": "processing"
}
```

### Anonymize Data
```bash
curl -X DELETE http://localhost:8000/api/v1/privacy/anonymize \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "message": "User data anonymized successfully"
}
```

## Error Examples

### Invalid Authentication
```bash
curl -X GET http://localhost:8000/api/v1/subscription \
  -H "Authorization: Bearer invalid_token"
```

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```

### Usage Limit Exceeded
```bash
curl -X POST http://localhost:8000/api/v1/finance/portfolio/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assets": [{"symbol": "AAPL", "weight": 1.0, "price": 150.0}]}'
```

**Response:**
```json
{
  "detail": "Usage limit exceeded for portfolio"
}
```

### Invalid Request Data
```bash
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440004",
    "message": "Hello"
  }'
```

**Response:**
```json
{
  "detail": "Cannot chat for another user"
}
```

## Complete Workflow Example

### 1. Authentication
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

echo "JWT Token: $TOKEN"
```

### 2. Check Subscription
```bash
curl -X GET http://localhost:8000/api/v1/subscription \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Use Finance Tools
```bash
curl -X POST http://localhost:8000/api/v1/finance/portfolio/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"symbol": "AAPL", "weight": 0.5, "price": 150.0},
      {"symbol": "GOOGL", "weight": 0.5, "price": 2500.0}
    ]
  }'
```

### 4. Chat with LLM
```bash
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "message": "Analyze my portfolio performance"
  }'
```

### 5. Check Usage
```bash
curl -X GET http://localhost:8000/api/v1/usage \
  -H "Authorization: Bearer $TOKEN"
```

## Notes

- Replace `YOUR_JWT_TOKEN` with actual token from login
- All examples assume local development server on port 8000
- User IDs in requests must match the authenticated user
- Rate limiting may apply to these endpoints
- Some responses may vary based on data and LLM responses