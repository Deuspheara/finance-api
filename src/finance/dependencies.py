from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.finance.tools.portfolio_analyzer import PortfolioAnalyzer
from src.subscriptions.dependencies import get_subscription_service
from src.subscriptions.services import SubscriptionService


async def get_portfolio_analyzer(
    session: AsyncSession = Depends(get_session),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
) -> PortfolioAnalyzer:
    return PortfolioAnalyzer(session, 0, subscription_service)  # user_id will be set in router
