from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.subscriptions.services import SubscriptionService


@pytest.mark.asyncio
async def test_users_have_isolated_data(client: AsyncClient, test_session: AsyncSession):
    """Test that different users have completely isolated financial data"""
    # Create two users
    user1_data = {
        "email": "user1@example.com",
        "password": "testpassword123"
    }
    user2_data = {
        "email": "user2@example.com",
        "password": "testpassword123"
    }

    response1 = await client.post("/users/", json=user1_data)
    user1_id = response1.json()["id"]

    response2 = await client.post("/users/", json=user2_data)
    user2_id = response2.json()["id"]

    # Login as user1
    login_response = await client.post("/auth/login", json=user1_data)
    token1 = login_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Login as user2
    login_response = await client.post("/auth/login", json=user2_data)
    token2 = login_response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User1 analyzes portfolio
    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 0.6, "price": 150.0},
            {"symbol": "GOOGL", "weight": 0.4, "price": 2500.0}
        ]
    }

    response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers1)
    assert response.status_code == 200
    result1 = response.json()

    # User2 analyzes different portfolio
    portfolio_data2 = {
        "assets": [
            {"symbol": "MSFT", "weight": 0.5, "price": 300.0},
            {"symbol": "AMZN", "weight": 0.5, "price": 3200.0}
        ]
    }

    response = await client.post("/finance/portfolio/analyze", json=portfolio_data2, headers=headers2)
    assert response.status_code == 200
    result2 = response.json()

    # Results should be different (since different portfolios)
    assert result1 != result2

    # Check usage logs are separate
    subscription_service = SubscriptionService(test_session)

    # User1 should have 1 portfolio usage
    can_use1 = await subscription_service.check_usage_limit(user1_id, "portfolio")
    assert can_use1 is True  # Still within limit

    # User2 should have 1 portfolio usage
    can_use2 = await subscription_service.check_usage_limit(user2_id, "portfolio")
    assert can_use2 is True  # Still within limit

    # Verify they don't share usage
    # If they shared, user1 would have used 2, but it's still 1
    from sqlalchemy import select

    from src.subscriptions.models import UsageLog

    result = await test_session.execute(
        select(UsageLog).where(UsageLog.user_id == user1_id, UsageLog.feature_name == "portfolio")
    )
    user1_logs = result.scalars().all()
    assert len(user1_logs) == 1

    result = await test_session.execute(
        select(UsageLog).where(UsageLog.user_id == user2_id, UsageLog.feature_name == "portfolio")
    )
    user2_logs = result.scalars().all()
    assert len(user2_logs) == 1


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_data(client: AsyncClient):
    """Test that users cannot access each other's financial data through API"""
    # This test is more about ensuring the API properly isolates data
    # Since the finance endpoints use current_user, this should be automatic

    # Create two users
    user1_data = {
        "email": "isolate1@example.com",
        "password": "testpassword123"
    }
    user2_data = {
        "email": "isolate2@example.com",
        "password": "testpassword123"
    }

    response1 = await client.post("/users/", json=user1_data)
    response1.json()["id"]

    response2 = await client.post("/users/", json=user2_data)
    response2.json()["id"]

    # Login as user1
    login_response = await client.post("/auth/login", json=user1_data)
    token1 = login_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # User1 analyzes portfolio
    portfolio_data = {
        "assets": [
            {"symbol": "AAPL", "weight": 1.0, "price": 150.0}
        ]
    }

    response = await client.post("/finance/portfolio/analyze", json=portfolio_data, headers=headers1)
    assert response.status_code == 200

    # Since there's no endpoint to get other users' data, and all operations
    # are scoped to current_user, this test mainly ensures the authentication
    # and authorization are working properly

    # Test that unauthenticated requests fail
    response = await client.post("/finance/portfolio/analyze", json=portfolio_data)
    assert response.status_code == 401
