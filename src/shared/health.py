from fastapi import APIRouter, Depends
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_session

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_session)):
    checks = {}

    try:
        # Check database connection
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    try:
        # Check Redis connection
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"warning: {str(e)}"

    # Consider ready if at least database is working
    is_ready = checks.get("database") == "ok"

    return {
        "status": "ready" if is_ready else "not ready",
        "checks": checks
    }

@router.get("/live")
async def liveness_check():
    return {"status": "alive"}
