from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.subscriptions.services import SubscriptionService


async def get_subscription_service(
    session: AsyncSession = Depends(get_session),
) -> SubscriptionService:
    return SubscriptionService(session)
