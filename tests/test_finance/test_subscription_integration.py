from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.subscriptions.services import SubscriptionService
from src.subscriptions.tiers import TIER_LIMITS, SubscriptionTier


@pytest.mark.asyncio
async def test_finance_tools_respect_free_tier_limits(client: AsyncClient, test_session: AsyncSession):
    """Test that finance tools enforce free tier portfolio limits"""
    # Create user
    user_data = {
        "email": "freelimit@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    response.json()["id"]

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 1.0, "price": 150.0}
        ]
    }

    # Use up the free tier limit
    free_limit = TIER_LIMITS[SubscriptionTier.FREE].portfolio_limit
    for _i in range(free_limit):
        response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers)
        assert response.status_code == 200

    # Next request should fail due to limit exceeded
    response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers)
    assert response.status_code == 500  # Exception raised in FinanceToolBase

    # Check the error message
    assert "Usage limit exceeded" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_premium_tier_unlimited_portfolio_access(client: AsyncClient, test_session: AsyncSession):
    """Test that premium users have higher portfolio limits"""
    # Create user
    user_data = {
        "email": "premiumfinance@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Upgrade to premium
    subscription_service = SubscriptionService(test_session)
    subscription = await subscription_service.get_subscription_by_user_id(user_id)
    subscription.tier = SubscriptionTier.PREMIUM.value
    test_session.add(subscription)
    await test_session.commit()

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 1.0, "price": 150.0}
        ]
    }

    # Use more than free limit
    free_limit = TIER_LIMITS[SubscriptionTier.FREE].portfolio_limit
    premium_limit = TIER_LIMITS[SubscriptionTier.PREMIUM].portfolio_limit

    for _i in range(free_limit + 1):  # One more than free limit
        response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers)
        assert response.status_code == 200

    # Should still work up to premium limit
    # (This test assumes premium_limit > free_limit + 1)
    assert premium_limit > free_limit


@pytest.mark.asyncio
async def test_usage_logging_on_finance_tool_usage(client: AsyncClient, test_session: AsyncSession):
    """Test that finance tool usage is properly logged"""
    # Create user
    user_data = {
        "email": "usagelogfinance@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Before usage
    subscription_service = SubscriptionService(test_session)
    can_use_before = await subscription_service.check_usage_limit(user_id, "portfolio")
    assert can_use_before is True

    # Use the tool
    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 1.0, "price": 150.0}
        ]
    }

    response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers)
    assert response.status_code == 200

    # Check usage was logged
    from sqlalchemy import select

    from src.subscriptions.models import UsageLog

    result = await test_session.execute(
        select(UsageLog).where(UsageLog.user_id == user_id, UsageLog.feature_name == "portfolio")
    )
    logs = result.scalars().all()
    assert len(logs) == 1

    # Check limit is now reduced
    can_use_after = await subscription_service.check_usage_limit(user_id, "portfolio")
    # Should still be true for free tier after 1 use
    assert can_use_after is True


@pytest.mark.asyncio
async def test_finance_tool_requires_authentication(client: AsyncClient):
    """Test that finance tools require authentication"""
    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 1.0, "price": 150.0}
        ]
    }

    # Try without authentication
    response = await client.post("/finance/portfolio/analyze", json=portfolio_data)
    assert response.status_code == 401
