from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import stripe
from stripe import SignatureVerificationError

from src.auth.router import router as auth_router
from src.core.config import settings
from src.core.database import create_db_and_tables
from src.core.exceptions import (
    BaseAPIError,
    api_exception_handler,
    general_exception_handler,
)
from src.finance.router import router as finance_router
from src.llm.router import router as llm_router
from src.privacy.router import router as privacy_router
from src.shared.health import router as health_router
from src.subscriptions.router import router as subscriptions_router
from src.subscriptions.tasks import process_stripe_event
from src.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.ENVIRONMENT == "development":
        await create_db_and_tables()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.RATE_LIMIT_TIMES} per {settings.RATE_LIMIT_SECONDS} seconds"
    ],
)

# Store limiter in app state for middleware access
app.state.limiter = limiter

# Add exception handlers
app.add_exception_handler(BaseAPIError, api_exception_handler)  # type: ignore
app.add_exception_handler(Exception, general_exception_handler)  # type: ignore
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Add middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(SlowAPIMiddleware)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(subscriptions_router, prefix="/api/v1", tags=["subscriptions"])
app.include_router(privacy_router, prefix="/api/v1", tags=["privacy"])
app.include_router(finance_router, prefix="/api/v1", tags=["finance"])
app.include_router(llm_router, prefix="/api/v1", tags=["llm"])


@app.post("/webhooks/stripe")
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


@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
