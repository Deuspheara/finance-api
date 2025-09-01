from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from src.core.exceptions import NotFoundError
from src.core.metrics import subscriptions_active_total
from src.subscriptions.models import Subscription, UsageLog
from src.subscriptions.tiers import TIER_LIMITS, SubscriptionTier


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_free_tier_for_user(self, user_id: UUID) -> Subscription:
        # Check if subscription already exists
        existing_subscription = await self.get_subscription_by_user_id(user_id)
        if existing_subscription:
            return existing_subscription

        subscription = Subscription(user_id=user_id, tier=SubscriptionTier.FREE.value)
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)

        # Increment metrics
        subscriptions_active_total.labels(tier=subscription.tier).inc()

        return subscription

    async def get_subscription_by_user_id(self, user_id: UUID) -> Subscription | None:
        statement = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def check_usage_limit(self, user_id: UUID, feature_name: str) -> bool:
        subscription = await self.get_subscription_by_user_id(user_id)
        if not subscription:
            raise NotFoundError("Subscription not found for user")

        tier = SubscriptionTier(subscription.tier)
        limits = TIER_LIMITS[tier]

        # Map feature_name to limit attribute
        if feature_name == "portfolio":
            limit = limits.portfolio_limit
        elif feature_name == "llm_requests":
            limit = limits.llm_requests_limit
        else:
            raise ValueError(f"Unknown feature: {feature_name}")

        # Count usage
        statement = select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id, UsageLog.feature_name == feature_name
        )
        result = await self.session.execute(statement)
        usage_count = result.scalar()

        return usage_count < limit

    async def log_usage(self, user_id: UUID, feature_name: str):
        usage_log = UsageLog(user_id=user_id, feature_name=feature_name)
        self.session.add(usage_log)
        await self.session.commit()
        await self.session.refresh(usage_log)
