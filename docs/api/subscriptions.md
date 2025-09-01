# Subscription Management API

## Overview

The subscription management API handles user subscription tiers, usage tracking, and limits. All endpoints require authentication and enforce user isolation.

## Endpoints

### Get Current Subscription

Retrieve the current user's subscription information.

**Endpoint:** `GET /api/v1/subscription`

**Authentication:** Required (JWT token)

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

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication
- `404 Not Found`: No subscription found for user

### Get Usage Logs

Retrieve the current user's usage logs for all features.

**Endpoint:** `GET /api/v1/usage`

**Authentication:** Required (JWT token)

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

## Subscription Tiers

### Free Tier
- **Portfolio Analyses:** 5 per month
- **LLM Requests:** 10 per month
- **Features:** Basic portfolio analysis, limited LLM chat

### Premium Tier
- **Portfolio Analyses:** 100 per month
- **LLM Requests:** 1000 per month
- **Features:** Advanced portfolio analysis, unlimited LLM chat, priority support

## Usage Limits

Usage is tracked per user per feature. When limits are exceeded:

- **Portfolio Analysis:** Returns `429 Too Many Requests` with message "Usage limit exceeded for portfolio"
- **LLM Requests:** Returns `429 Too Many Requests` with message "Usage limit exceeded for LLM requests"

Limits reset monthly based on subscription creation date.

## Subscription Changes

Subscription tier changes are handled through Stripe webhooks:

- **Upgrade:** Processed via Stripe webhook, updates user tier to "premium"
- **Downgrade:** Processed via Stripe webhook, updates user tier to "free"
- **Cancellation:** Processed via Stripe webhook, maintains current tier until period ends

## Data Models

### SubscriptionResponse
```python
{
  "id": UUID,                  # Subscription ID
  "user_id": UUID,             # User ID
  "tier": str,                 # "free" or "premium"
  "created_at": datetime,      # ISO 8601 timestamp
  "updated_at": datetime,      # ISO 8601 timestamp (optional)
  "stripe_customer_id": str    # Stripe customer ID (optional)
}
```

### UsageLogResponse
```python
{
  "id": UUID,                  # Usage log ID
  "user_id": UUID,             # User ID
  "feature_name": str,         # "portfolio" or "llm_requests"
  "timestamp": datetime        # ISO 8601 timestamp
}
```

## Notes

- All users start with a free tier subscription automatically upon registration
- Usage limits are enforced at the API level before processing requests
- Subscription changes take effect immediately via Stripe webhooks
- Usage logs are kept for audit and analytics purposes