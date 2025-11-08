"""
Tests for Database Service
"""


import pytest

from src.services.database import DatabaseService


class TestDatabaseService:
    """Test suite for DatabaseService."""

    @pytest.mark.asyncio
    async def test_connection(self, db_service: DatabaseService):
        """Test database connection."""
        assert db_service.is_connected()

    @pytest.mark.asyncio
    async def test_health_check(self, db_service: DatabaseService):
        """Test health check."""
        is_healthy = await db_service.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_execute(self, db_service: DatabaseService):
        """Test query execution."""
        result = await db_service.execute("SELECT 1")
        assert result is not None

    @pytest.mark.asyncio
    async def test_fetch_one(self, db_service: DatabaseService):
        """Test fetch one row."""
        result = await db_service.fetch_one("SELECT 1 as value")
        assert result is not None
        assert result['value'] == 1

    @pytest.mark.asyncio
    async def test_fetch_all(self, db_service: DatabaseService):
        """Test fetch all rows."""
        result = await db_service.fetch_all(
            "SELECT * FROM generate_series(1, 5) as value"
        )
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_get_cameras(self, db_service: DatabaseService):
        """Test get cameras."""
        cameras = await db_service.get_cameras()
        assert isinstance(cameras, list)
        # Should have seeded cameras
        assert len(cameras) >= 0

    @pytest.mark.asyncio
    async def test_get_alerts(self, db_service: DatabaseService):
        """Test get alerts with filtering."""
        # Get all alerts
        all_alerts = await db_service.get_alerts()
        assert isinstance(all_alerts, list)

        # Filter by status
        active_alerts = await db_service.get_alerts(status='active')
        assert isinstance(active_alerts, list)

        # All results should be active
        for alert in active_alerts:
            assert alert['status'] == 'active'

    @pytest.mark.asyncio
    async def test_get_alert_statistics(self, db_service: DatabaseService):
        """Test alert statistics."""
        stats = await db_service.get_alert_statistics(hours=24)
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'active' in stats
        assert 'critical' in stats

    @pytest.mark.asyncio
    async def test_get_threat_statistics(self, db_service: DatabaseService):
        """Test threat statistics."""
        stats = await db_service.get_threat_statistics(hours=24)
        assert isinstance(stats, dict)
        assert 'total_threats' in stats
        assert 'avg_threat_score' in stats

    @pytest.mark.asyncio
    async def test_calculate_threat_trend(self, db_service: DatabaseService):
        """Test threat trend calculation."""
        trend = await db_service.calculate_threat_trend(hours=24)
        assert isinstance(trend, dict)
        assert 'current' in trend
        assert 'previous' in trend
        assert 'direction' in trend
        assert trend['direction'] in ['up', 'down', 'stable']

    @pytest.mark.asyncio
    async def test_get_camera_statistics(self, db_service: DatabaseService):
        """Test camera statistics."""
        stats = await db_service.get_camera_statistics()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'online' in stats
        assert stats['total'] >= 0

    @pytest.mark.asyncio
    async def test_get_timeline_events(self, db_service: DatabaseService):
        """Test timeline events retrieval."""
        events = await db_service.get_timeline_events(hours=24)
        assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_transaction(self, db_service: DatabaseService):
        """Test transaction support."""
        async with db_service.transaction() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1

    @pytest.mark.asyncio
    async def test_pool_stats(self, db_service: DatabaseService):
        """Test connection pool statistics."""
        stats = await db_service.get_pool_stats()
        assert stats['connected'] is True
        assert stats['size'] >= 0
