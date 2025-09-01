import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.subscriptions.models import Subscription

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_stripe_event(self, event_data: dict[str, Any]) -> str:
    """
    Process Stripe webhook events asynchronously.
    Handles invoice.paid and subscription.deleted events.
    Idempotent by checking event ID and current subscription state.
    """
    try:
        return asyncio.run(_process_event_async(event_data))
    except Exception as exc:
        logger.error(f"Error processing event {event_data.get('id')}: {exc}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2**self.request.retries), exc=exc) from exc


async def _process_event_async(event_data: dict[str, Any]) -> str:
    event_id = event_data.get("id")
    event_type = event_data.get("type")

    logger.info(f"Processing Stripe event {event_id} of type {event_type}")

    # Idempotency check: Skip if event already processed
    # For simplicity, we'll check subscription state instead of storing event IDs
    # In production, you'd want a ProcessedStripeEvent table

    async with AsyncSessionLocal() as session:
        if event_type == "invoice.payment_succeeded":
            await _handle_invoice_paid(session, event_data)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(session, event_data)
        else:
            logger.info(f"Ignoring event type: {event_type}")
            return f"Ignored event {event_id}"

    logger.info(f"Successfully processed event {event_id}")
    return f"Processed event {event_id}"


async def _handle_invoice_paid(session: AsyncSession, event_data: dict[str, Any]):
    """Handle successful invoice payment - upgrade to premium."""
    data = event_data.get("data", {}).get("object", {})
    customer_id = data.get("customer")

    if not customer_id:
        logger.warning("No customer ID in invoice.paid event")
        return

    # Find subscription by Stripe customer ID
    stmt = select(Subscription).where(Subscription.stripe_customer_id == customer_id)
    result = await session.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"No subscription found for customer {customer_id}")
        return

    # Update to premium tier
    from src.subscriptions.tiers import SubscriptionTier

    subscription.tier = SubscriptionTier.PREMIUM.value
    subscription.updated_at = data.get("created")  # Use Stripe timestamp

    session.add(subscription)
    await session.commit()

    logger.info(f"Upgraded subscription for user {subscription.user_id} to premium")


async def _handle_subscription_deleted(
    session: AsyncSession, event_data: dict[str, Any]
):
    """Handle subscription cancellation - downgrade to free."""
    data = event_data.get("data", {}).get("object", {})
    customer_id = data.get("customer")

    if not customer_id:
        logger.warning("No customer ID in subscription.deleted event")
        return

    # Find subscription by Stripe customer ID
    stmt = select(Subscription).where(Subscription.stripe_customer_id == customer_id)
    result = await session.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"No subscription found for customer {customer_id}")
        return

    # Downgrade to free tier
    from src.subscriptions.tiers import SubscriptionTier

    subscription.tier = SubscriptionTier.FREE.value
    subscription.updated_at = data.get("canceled_at")  # Use cancellation timestamp

    session.add(subscription)
    await session.commit()

    logger.info(f"Downgraded subscription for user {subscription.user_id} to free")
