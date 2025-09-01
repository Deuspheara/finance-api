from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.subscriptions.models import UsageLog
from src.subscriptions.services import SubscriptionService
from src.subscriptions.tiers import TIER_LIMITS, SubscriptionTier


@pytest.mark.asyncio
async def test_free_tier_portfolio_limit(
    client: AsyncClient, test_session: AsyncSession
):
    """Test that free tier users are limited to 5 portfolios"""
    # Create user
    user_data = {"email": "freelimit@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    subscription_service = SubscriptionService(test_session)

    # Check initial limit (should be within limit)
    can_use = await subscription_service.check_usage_limit(user_id, "portfolio")
    assert can_use is True

    # Log usage up to the limit
    for _i in range(TIER_LIMITS[SubscriptionTier.FREE].portfolio_limit):
        await subscription_service.log_usage(user_id, "portfolio")

    # Should now be at limit
    can_use = await subscription_service.check_usage_limit(user_id, "portfolio")
    assert can_use is False


@pytest.mark.asyncio
async def test_premium_tier_unlimited_access(
    client: AsyncClient, test_session: AsyncSession
):
    """Test that premium tier users have higher limits"""
    # Create user
    user_data = {"email": "premiumlimit@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    subscription_service = SubscriptionService(test_session)

    # Upgrade to premium
    subscription = await subscription_service.get_subscription_by_user_id(user_id)
    subscription.tier = SubscriptionTier.PREMIUM.value
    test_session.add(subscription)
    await test_session.commit()

    # Should be able to use more than free limit
    free_limit = TIER_LIMITS[SubscriptionTier.FREE].portfolio_limit
    premium_limit = TIER_LIMITS[SubscriptionTier.PREMIUM].portfolio_limit

    # Log usage up to free limit
    for _i in range(free_limit):
        await subscription_service.log_usage(user_id, "portfolio")

    # Should still be within premium limit
    can_use = await subscription_service.check_usage_limit(user_id, "portfolio")
    assert can_use is True

    # Continue logging up to premium limit
    for _i in range(premium_limit - free_limit):
        await subscription_service.log_usage(user_id, "portfolio")

    # Should now be at limit
    can_use = await subscription_service.check_usage_limit(user_id, "portfolio")
    assert can_use is False


@pytest.mark.asyncio
async def test_llm_requests_limit(client: AsyncClient, test_session: AsyncSession):
    """Test LLM request limits for different tiers"""
    # Create free user
    user_data = {"email": "llmfree@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    subscription_service = SubscriptionService(test_session)

    # Log LLM requests up to free limit
    for _i in range(TIER_LIMITS[SubscriptionTier.FREE].llm_requests_limit):
        await subscription_service.log_usage(user_id, "llm_requests")

    # Should be at limit
    can_use = await subscription_service.check_usage_limit(user_id, "llm_requests")
    assert can_use is False


@pytest.mark.asyncio
async def test_usage_logging_creates_records(
    client: AsyncClient, test_session: AsyncSession
):
    """Test that usage logging creates proper records"""
    # Create user
    user_data = {"email": "usagelog@example.com", "password": "testpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    subscription_service = SubscriptionService(test_session)

    # Log some usage
    await subscription_service.log_usage(user_id, "portfolio")
    await subscription_service.log_usage(user_id, "llm_requests")

    # Check usage logs were created
    from sqlalchemy import select

    result = await test_session.execute(
        select(UsageLog).where(UsageLog.user_id == user_id)
    )
    logs = result.scalars().all()

    assert len(logs) == 2
    features = [log.feature_name for log in logs]
    assert "portfolio" in features
    assert "llm_requests" in features
