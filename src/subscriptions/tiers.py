from enum import Enum
from dataclasses import dataclass

class SubscriptionTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

@dataclass
class TierLimits:
    portfolio_limit: int
    llm_requests_limit: int

TIER_LIMITS = {
    SubscriptionTier.FREE: TierLimits(portfolio_limit=5, llm_requests_limit=10),
    SubscriptionTier.PREMIUM: TierLimits(portfolio_limit=100, llm_requests_limit=1000)
}