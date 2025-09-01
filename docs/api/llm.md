# LLM Chat API

## Overview

The LLM chat API provides conversational AI capabilities with context management and usage limits. All endpoints require authentication and enforce user isolation.

## Endpoints

### Chat with LLM

Send a message to the LLM and receive a response with conversation context.

**Endpoint:** `POST /api/v1/llm/chat`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "message": "What are the best investment strategies for beginners?"
}
```

**Response:**
```json
{
  "response": "For beginners, I recommend starting with a diversified portfolio through index funds or ETFs. Focus on long-term investing rather than trying to time the market. Consider your risk tolerance and investment timeline before making decisions."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request data or user_id mismatch
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Attempting to chat for another user
- `429 Too Many Requests`: Usage limit exceeded for LLM requests

## Usage Limits

LLM chat requests are limited by subscription tier:

- **Free Tier:** 10 requests per month
- **Premium Tier:** 1000 requests per month

Limits reset monthly based on subscription creation date.

## Conversation Context

The system maintains conversation context per user:

- **Context Storage:** Messages are stored in memory with database logging
- **Context Length:** Maintains full conversation history for the session
- **Isolation:** Each user has their own conversation context
- **Persistence:** Conversation logs are saved to database for audit purposes

## Data Models

### LLMRequest
```python
{
  "user_id": UUID,   # Must match authenticated user ID
  "message": str     # User's message (max length validated by LLM provider)
}
```

### LLMResponse
```python
{
  "response": str    # LLM-generated response
}
```

## Validation Rules

- **user_id:** Must match the authenticated user's ID
- **message:** Must be non-empty string
- **Length Limits:** Subject to LLM provider's token limits

## LLM Integration

The system integrates with OpenRouter API:

- **Provider:** OpenRouter (supports multiple LLM models)
- **Default Model:** openai/gpt-4o
- **Fallback:** Automatic fallback to available models if primary fails
- **Rate Limiting:** Respects both user limits and provider rate limits

## Conversation Logging

Each interaction is logged:

- **Database Storage:** Messages and responses saved to ConversationLog table
- **Audit Trail:** Complete conversation history for compliance
- **Usage Tracking:** Each request increments monthly usage counter
- **Performance:** Asynchronous logging doesn't block response

## Error Handling

- **Provider Errors:** Automatic retry with fallback models
- **Rate Limits:** Clear error messages for user limits
- **Authentication:** Strict user isolation enforcement
- **Input Validation:** Comprehensive request validation

## Notes

- Responses are generated synchronously
- Conversation context persists across requests within the same session
- Large conversations may impact memory usage
- All conversations are logged for quality and compliance purposes
- The system supports multiple LLM models through OpenRouter