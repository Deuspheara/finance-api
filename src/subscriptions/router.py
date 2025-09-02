from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import stripe
from stripe import SignatureVerificationError

from src.auth.dependencies import get_current_active_user
from src.core.config import settings
from src.core.database import get_session
from src.subscriptions.dependencies import get_subscription_service
from src.subscriptions.models import UsageLog
from src.subscriptions.schemas import SubscriptionResponse, UsageLogResponse
from src.subscriptions.services import SubscriptionService
from src.subscriptions.tasks import process_stripe_event
from src.users.models import User

router = APIRouter()


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="User ID is required")
    subscription = await subscription_service.get_subscription_by_user_id(
        current_user.id
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return SubscriptionResponse.model_validate(subscription)


@router.get("/usage", response_model=list[UsageLogResponse])
async def get_usage_logs(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    statement = select(UsageLog).where(UsageLog.user_id == current_user.id)
    result = await session.execute(statement)
    usage_logs = result.scalars().all()
    return [UsageLogResponse.model_validate(log) for log in usage_logs]


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks by enqueuing Celery tasks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload") from e
    except SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    # Enqueue the task for background processing
    process_stripe_event.delay(event)

    return {"status": "accepted"}
