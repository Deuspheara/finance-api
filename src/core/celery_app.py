from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "finance_tool_api",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.subscriptions.tasks", "src.privacy.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_queue="finance_tool_api",
    task_routes={
        "src.subscriptions.tasks.process_stripe_event": {"queue": "webhooks"},
        "src.privacy.tasks.generate_user_data_export": {"queue": "privacy"},
    },
)

# Import tasks to register them
from src.subscriptions import tasks  # noqa
from src.privacy import tasks  # noqa