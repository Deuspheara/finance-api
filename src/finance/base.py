from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.metrics import finance_tool_usage_total
from src.subscriptions.services import SubscriptionService


class FinanceToolBase(ABC):
    feature_name: str = "finance_tool"  # Default, override in subclasses

    def __init__(
        self,
        session: AsyncSession,
        user_id: UUID,
        subscription_service: SubscriptionService,
    ):
        self.session = session
        self.user_id = user_id
        self.subscription_service = subscription_service

    async def run(self, *args, **kwargs):
        # Check usage limit
        if not await self.subscription_service.check_usage_limit(
            self.user_id, self.feature_name
        ):
            raise Exception("Usage limit exceeded")

        # Execute tool
        result = await self._execute(*args, **kwargs)

        # Log usage
        await self.subscription_service.log_usage(self.user_id, self.feature_name)

        # Increment metrics
        finance_tool_usage_total.labels(
            tool_name=self.feature_name, user_id=str(self.user_id)
        ).inc()

        return result

    @abstractmethod
    async def _execute(self, *args, **kwargs):
        pass
