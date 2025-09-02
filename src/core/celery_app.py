import os

from celery import Celery  # type: ignore

from src.core.config import settings

# Use memory broker for tests to avoid Redis dependency
is_test = os.environ.get("REDIS_URL", "").startswith("redis://fake-")
broker_url = "memory://" if is_test else settings.REDIS_URL
backend_url = "cache+memory://" if is_test else settings.REDIS_URL

celery_app = Celery(
    "finance_tool_api",
    broker=broker_url,
    backend=backend_url,
    include=["src.subscriptions.tasks", "src.privacy.tasks"],
)

# Celery configuration
config = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_acks_late": True,
    "task_reject_on_worker_lost": True,
    "worker_prefetch_multiplier": 1,
    "task_default_queue": "finance_tool_api",
    "task_routes": {
        "src.subscriptions.tasks.process_stripe_event": {"queue": "webhooks"},
        "src.privacy.tasks.generate_user_data_export": {"queue": "privacy"},
    },
}

# Enable eager execution for tests (run tasks synchronously)
if is_test:
    config.update(
        {
            "task_always_eager": True,
            "task_eager_propagates": True,
        }
    )

celery_app.conf.update(**config)

# Import tasks to register them
from src.subscriptions import tasks as subscription_tasks  # noqa
from src.privacy import tasks as privacy_tasks  # noqa
