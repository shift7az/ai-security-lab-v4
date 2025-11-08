"""
Tests for Cache Service
"""

import pytest

from src.services.cache import CacheService


class TestCacheService:
    """Test suite for CacheService."""

    @pytest.mark.asyncio
    async def test_connection(self, cache_service: CacheService):
        """Test cache connection."""
        assert cache_service.is_connected()

    @pytest.mark.asyncio
    async def test_health_check(self, cache_service: CacheService):
        """Test health check."""
        is_healthy = await cache_service.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_set_get(self, cache_service: CacheService):
        """Test set and get operations."""
        key = "test_key"
        value = "test_value"

        await cache_service.set(key, value)
        result = await cache_service.get(key)

        assert result == value

        # Cleanup
        await cache_service.delete(key)

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache_service: CacheService):
        """Test set with TTL."""
        key = "test_ttl_key"
        value = "test_value"
        ttl = 60

        await cache_service.set(key, value, ttl=ttl)
        result = await cache_service.get(key)
        assert result == value

        # Check TTL
        remaining_ttl = await cache_service.ttl(key)
        assert remaining_ttl > 0
        assert remaining_ttl <= ttl

        # Cleanup
        await cache_service.delete(key)

    @pytest.mark.asyncio
    async def test_json_operations(self, cache_service: CacheService):
        """Test JSON set and get."""
        key = "test_json"
        data = {"name": "test", "value": 123, "active": True}

        await cache_service.set_json(key, data)
        result = await cache_service.get_json(key)

        assert result == data

        # Cleanup
        await cache_service.delete(key)

    @pytest.mark.asyncio
    async def test_exists(self, cache_service: CacheService):
        """Test key existence check."""
        key = "test_exists"

        # Should not exist
        exists = await cache_service.exists(key)
        assert exists is False

        # Create key
        await cache_service.set(key, "value")
        exists = await cache_service.exists(key)
        assert exists is True

        # Cleanup
        await cache_service.delete(key)

    @pytest.mark.asyncio
    async def test_delete(self, cache_service: CacheService):
        """Test delete operation."""
        key = "test_delete"

        await cache_service.set(key, "value")
        assert await cache_service.exists(key)

        deleted = await cache_service.delete(key)
        assert deleted is True
        assert not await cache_service.exists(key)
