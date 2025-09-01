import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from src.subscriptions.services import SubscriptionService
from src.subscriptions.tiers import SubscriptionTier, TIER_LIMITS
from src.llm.models import ConversationLog


@pytest.mark.asyncio
async def test_llm_chat_with_subscription_check(client: AsyncClient, test_session: AsyncSession, respx_mock):
    """Test LLM chat functionality with subscription limits"""
    # Create user
    user_data = {
        "email": "llmuser@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock OpenRouter API response
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Hello! This is a test response from the LLM."
                }
            }
        ]
    }

    respx_mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
        json=mock_response,
        status_code=200
    )

    # Send chat message
    chat_data = {
        "user_id": user_id,
        "message": "Hello, can you help me with finance?"
    }

    response = await client.post("/llm/chat", json=chat_data, headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert "response" in result
    assert result["response"] == "Hello! This is a test response from the LLM."

    # Check conversation was logged
    from sqlalchemy import select
    result = await test_session.execute(
        select(ConversationLog).where(ConversationLog.user_id == user_id)
    )
    logs = result.scalars().all()
    assert len(logs) == 1
    assert logs[0].message == "Hello, can you help me with finance?"
    assert logs[0].response == "Hello! This is a test response from the LLM."

    # Check usage was logged
    subscription_service = SubscriptionService(test_session)
    can_use = await subscription_service.check_usage_limit(user_id, "llm_requests")
    # Should still be true after 1 use for free tier
    assert can_use is True


@pytest.mark.asyncio
async def test_llm_usage_limit_exceeded(client: AsyncClient, test_session: AsyncSession, respx_mock):
    """Test that LLM requests are limited by subscription"""
    # Create user
    user_data = {
        "email": "llmlimit@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    subscription_service = SubscriptionService(test_session)

    # Mock OpenRouter API
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    }

    respx_mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
        json=mock_response,
        status_code=200
    )

    chat_data = {
        "user_id": user_id,
        "message": "Test message"
    }

    # Use up the free tier limit
    free_limit = TIER_LIMITS[SubscriptionTier.FREE].llm_requests_limit
    for i in range(free_limit):
        response = await client.post("/llm/chat", json=chat_data, headers=headers)
        assert response.status_code == 200

    # Next request should fail
    response = await client.post("/llm/chat", json=chat_data, headers=headers)
    assert response.status_code == 429
    assert "Usage limit exceeded" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_llm_chat_user_isolation(client: AsyncClient, test_session: AsyncSession, respx_mock):
    """Test that LLM conversations are isolated per user"""
    # Create two users
    user1_data = {
        "email": "llmuser1@example.com",
        "password": "testpassword123"
    }
    user2_data = {
        "email": "llmuser2@example.com",
        "password": "testpassword123"
    }

    response1 = await client.post("/users/", json=user1_data)
    user1_id = response1.json()["id"]

    response2 = await client.post("/users/", json=user2_data)
    user2_id = response2.json()["id"]

    # Login both users
    login1 = await client.post("/auth/login", json=user1_data)
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    login2 = await client.post("/auth/login", json=user2_data)
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Mock OpenRouter API
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Response for user"
                }
            }
        ]
    }

    respx_mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
        json=mock_response,
        status_code=200
    )

    # User1 chats
    chat_data1 = {
        "user_id": user1_id,
        "message": "Hello from user1"
    }

    response = await client.post("/llm/chat", json=chat_data1, headers=headers1)
    assert response.status_code == 200

    # User2 chats
    chat_data2 = {
        "user_id": user2_id,
        "message": "Hello from user2"
    }

    response = await client.post("/llm/chat", json=chat_data2, headers=headers2)
    assert response.status_code == 200

    # Check separate conversation logs
    from sqlalchemy import select
    result1 = await test_session.execute(
        select(ConversationLog).where(ConversationLog.user_id == user1_id)
    )
    logs1 = result1.scalars().all()
    assert len(logs1) == 1
    assert logs1[0].message == "Hello from user1"

    result2 = await test_session.execute(
        select(ConversationLog).where(ConversationLog.user_id == user2_id)
    )
    logs2 = result2.scalars().all()
    assert len(logs2) == 1
    assert logs2[0].message == "Hello from user2"


@pytest.mark.asyncio
async def test_llm_chat_requires_authentication(client: AsyncClient, respx_mock):
    """Test that LLM chat requires authentication"""
    # Mock OpenRouter API
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    }

    respx_mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
        json=mock_response,
        status_code=200
    )

    chat_data = {
        "user_id": 1,
        "message": "Test message"
    }

    # Try without authentication
    response = await client.post("/llm/chat", json=chat_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_llm_chat_user_validation(client: AsyncClient, respx_mock):
    """Test that users can only chat for themselves"""
    # Create two users
    user1_data = {
        "email": "llmval1@example.com",
        "password": "testpassword123"
    }
    user2_data = {
        "email": "llmval2@example.com",
        "password": "testpassword123"
    }

    response1 = await client.post("/users/", json=user1_data)
    user1_id = response1.json()["id"]

    response2 = await client.post("/users/", json=user2_data)
    user2_id = response2.json()["id"]

    # Login as user1
    login_response = await client.post("/auth/login", json=user1_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock OpenRouter API
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    }

    respx_mock.post("https://openrouter.ai/api/v1/chat/completions").respond(
        json=mock_response,
        status_code=200
    )

    # Try to chat for user2
    chat_data = {
        "user_id": user2_id,
        "message": "Hello"
    }

    response = await client.post("/llm/chat", json=chat_data, headers=headers)
    assert response.status_code == 403