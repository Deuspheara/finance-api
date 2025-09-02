import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Set test environment variables before importing the app
os.environ["REDIS_URL"] = "redis://fake-redis:6379"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["ENVIRONMENT"] = "development"

from src.core.database import get_session
from src.main import app

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Event loop is managed by pytest-asyncio


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    logger.debug(f"test_engine: Starting fixture, event loop: {id(asyncio.get_running_loop())}")
    # Disable connection pooling to avoid event loop conflicts
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=None  # Disable pooling
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.debug(f"test_engine: Yielding engine, event loop: {id(asyncio.get_running_loop())}")
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()
    logger.debug(f"test_engine: Disposed engine, event loop: {id(asyncio.get_running_loop())}")


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    logger.debug(f"test_session: Starting fixture, event loop: {id(asyncio.get_running_loop())}")
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    session = async_session()
    try:
        logger.debug(f"test_session: Created session, event loop: {id(asyncio.get_running_loop())}")
        # Start a transaction for test isolation
        await session.begin()
        logger.debug(f"test_session: Yielding session, event loop: {id(asyncio.get_running_loop())}")
        yield session
    finally:
        # Rollback the transaction to clean up test data
        await session.rollback()
        await session.close()
        logger.debug(f"test_session: Closed session, event loop: {id(asyncio.get_running_loop())}")


@pytest_asyncio.fixture
async def client(test_session):
    logger.debug(f"client: Starting fixture, event loop: {id(asyncio.get_running_loop())}")
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            logger.debug(f"client: Yielding client, event loop: {id(asyncio.get_running_loop())}")
            yield client
        finally:
            app.dependency_overrides.clear()
            logger.debug(f"client: Closed client and cleared overrides, event loop: {id(asyncio.get_running_loop())}")


# Mock Celery tasks to avoid Redis connections in tests

# Mock the Celery app before any imports
mock_task = MagicMock()
mock_result = MagicMock()
mock_result.id = "test-task-id"
mock_result.ready.return_value = True
mock_result.get.return_value = "Task completed successfully"

mock_task.delay = MagicMock(return_value=mock_result)
mock_task.apply_async = MagicMock(return_value=mock_result)

# Create a mock Celery app that doesn't try to connect to Redis
mock_celery_app = MagicMock()
mock_celery_app.task = MagicMock(return_value=mock_task)

# Patch the celery module in sys.modules before it gets imported
sys.modules['src.core.celery_app'] = MagicMock()
sys.modules['src.core.celery_app'].celery_app = mock_celery_app
