"""
Pytest fixtures for AI Security Lab tests
"""

import asyncio
from typing import AsyncGenerator

import pytest

from src.config.settings import Settings
from src.services.cache import CacheService
from src.services.database import DatabaseService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Create settings instance."""
    return Settings()


@pytest.fixture(scope="session")
async def db_service(settings: Settings) -> AsyncGenerator[DatabaseService, None]:
    """
    Create database service instance.
    Note: Requires database to be running.
    """
    db = DatabaseService(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password
    )

    try:
        await db.connect()
        yield db
    finally:
        await db.disconnect()


@pytest.fixture(scope="session")
async def cache_service(settings: Settings) -> AsyncGenerator[CacheService, None]:
    """
    Create cache service instance.
    Note: Requires Redis to be running.
    """
    cache = CacheService(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db
    )

    try:
        await cache.connect()
        yield cache
    finally:
        await cache.disconnect()


@pytest.fixture
async def clean_test_data(db_service: DatabaseService):
    """
    Clean test data before and after tests.
    Use for tests that modify database.
    """
    # Setup: Could clean or setup test data
    yield
    # Teardown: Clean up test data
    pass
