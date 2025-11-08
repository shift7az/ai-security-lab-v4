"""
Database Service for AI Security Lab v4.0
Handles all database operations with AsyncPG and TimescaleDB
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Async database service with connection pooling and TimescaleDB support.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        min_pool_size: int = 5,
        max_pool_size: int = 20,
        command_timeout: float = 60.0
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.command_timeout = command_timeout

        self.pool: Optional[Pool] = None
        self._is_connected = False

    async def connect(self) -> None:
        """
        Establish database connection pool.
        """
        try:
            logger.info(f"Connecting to database: {self.host}:{self.port}/{self.database}")

            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=self.command_timeout,
                timeout=30.0,  # Connection timeout
            )

            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

            self._is_connected = True
            logger.info("✅ Database connection pool established")

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Close database connection pool.
        """
        try:
            if self.pool:
                await self.pool.close()
                self._is_connected = False
                logger.info("Database connection pool closed")
        except Exception as e:
            logger.error(f"Error closing database pool: {e}")

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected and self.pool is not None

    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            async with db.transaction():
                await db.execute(query1)
                await db.execute(query2)
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute(self, query: str, *args) -> str:
        """
        Execute a query and return status.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Query status string
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        try:
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Dictionary of column:value or None
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            raise

    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            List of dictionaries
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            raise

    async def execute_many(self, query: str, args_list: List[tuple]) -> None:
        """
        Execute query multiple times with different parameters.
        
        Args:
            query: SQL query
            args_list: List of parameter tuples
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        try:
            async with self.pool.acquire() as conn:
                await conn.executemany(query, args_list)
        except Exception as e:
            logger.error(f"Execute many failed: {e}")
            raise

    # ========================================================================
    # Domain-Specific Query Methods
    # ========================================================================

    async def get_cameras(self) -> List[Dict[str, Any]]:
        """Get all cameras with their current status."""
        query = """
            SELECT 
                id,
                name,
                location,
                status,
                stream_url,
                snapshot_url,
                uptime_percentage,
                metadata,
                created_at,
                updated_at
            FROM cameras
            ORDER BY name
        """
        return await self.fetch_all(query)

    async def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get specific camera by ID."""
        query = """
            SELECT 
                id,
                name,
                location,
                status,
                stream_url,
                snapshot_url,
                uptime_percentage,
                metadata,
                created_at,
                updated_at
            FROM cameras
            WHERE id = $1
        """
        return await self.fetch_one(query, camera_id)

    async def get_camera_threat_count(self, camera_id: str, hours: int = 24) -> int:
        """Get threat count for camera in specified time period."""
        query = """
            SELECT COUNT(*) as count
            FROM intelligence_results
            WHERE camera_id = $1
            AND timestamp > NOW() - INTERVAL '%s hours'
            AND threat_score > 0.3
        """
        result = await self.fetch_one(query % hours, camera_id)
        return result['count'] if result else 0

    async def get_detections(
        self,
        camera_id: str,
        since: datetime,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent detections for a camera."""
        query = """
            SELECT 
                detection_id,
                camera_id,
                timestamp,
                threat_score,
                threat_level,
                ai_models_used,
                insights,
                processing_time_ms
            FROM intelligence_results
            WHERE camera_id = $1
            AND timestamp > $2
            ORDER BY timestamp DESC
            LIMIT $3
        """
        return await self.fetch_all(query, camera_id, since, limit)

    async def get_threats(
        self,
        min_score: float,
        since: datetime,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent threats above minimum score."""
        query = """
            SELECT 
                detection_id,
                camera_id,
                timestamp,
                threat_score,
                threat_level,
                ai_models_used,
                insights
            FROM intelligence_results
            WHERE timestamp > $1
            AND threat_score >= $2
            ORDER BY threat_score DESC, timestamp DESC
            LIMIT $3
        """
        return await self.fetch_all(query, since, min_score, limit)

    async def store_intelligence_result(
        self,
        detection_id: str,
        camera_id: str,
        timestamp: datetime,
        threat_score: float,
        threat_level: str,
        ai_models_used: List[str],
        insights: Dict[str, Any],
        processing_time_ms: float
    ) -> None:
        """Store intelligence analysis result."""
        query = """
            INSERT INTO intelligence_results (
                detection_id, camera_id, timestamp, threat_score,
                threat_level, ai_models_used, insights, processing_time_ms
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        await self.execute(
            query,
            detection_id,
            camera_id,
            timestamp,
            threat_score,
            threat_level,
            ai_models_used,
            insights,
            processing_time_ms
        )

    async def get_alerts(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        camera_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering."""
        conditions = ["1=1"]
        params = []
        param_count = 0

        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)

        if priority:
            param_count += 1
            conditions.append(f"priority = ${param_count}")
            params.append(priority)

        if camera_id:
            param_count += 1
            conditions.append(f"camera_id = ${param_count}")
            params.append(camera_id)

        param_count += 1

        query = f"""
            SELECT 
                a.id,
                a.camera_id,
                c.name as camera_name,
                a.threat_level,
                a.priority,
                a.message,
                a.description,
                a.timestamp,
                a.status,
                a.acknowledged_by,
                a.acknowledged_at,
                a.resolved_by,
                a.resolved_at,
                a.resolution_notes,
                a.detection_id,
                i.threat_score
            FROM alerts a
            LEFT JOIN cameras c ON a.camera_id = c.id
            LEFT JOIN intelligence_results i ON a.detection_id = i.detection_id
            WHERE {' AND '.join(conditions)}
            ORDER BY a.priority DESC, a.timestamp DESC
            LIMIT ${param_count}
        """

        return await self.fetch_all(query, *params, limit)

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert."""
        query = """
            UPDATE alerts
            SET status = 'acknowledged',
                acknowledged_by = $2,
                acknowledged_at = NOW()
            WHERE id = $1
            AND status = 'active'
            RETURNING id
        """
        result = await self.fetch_one(query, alert_id, user_id)
        return result is not None

    async def resolve_alert(self, alert_id: str, user_id: str, notes: str = "") -> bool:
        """Resolve an alert with notes."""
        query = """
            UPDATE alerts
            SET status = 'resolved',
                resolved_by = $2,
                resolved_at = NOW(),
                resolution_notes = $3
            WHERE id = $1
            AND status IN ('active', 'acknowledged')
            RETURNING id
        """
        result = await self.fetch_one(query, alert_id, user_id, notes)
        return result is not None

    async def create_alert(
        self,
        alert_id: str,
        camera_id: str,
        detection_id: str,
        threat_level: str,
        priority: str,
        message: str,
        description: str = ""
    ) -> None:
        """Create a new alert."""
        query = """
            INSERT INTO alerts (
                id, camera_id, detection_id, threat_level,
                priority, message, description, timestamp, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), 'active')
        """
        await self.execute(
            query,
            alert_id,
            camera_id,
            detection_id,
            threat_level,
            priority,
            message,
            description
        )

    async def get_timeline_events(
        self,
        hours: int = 24,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get timeline events."""
        conditions = [f"timestamp > NOW() - INTERVAL '{hours} hours'"]
        params = []
        param_count = 0

        if event_type and event_type != 'all':
            param_count += 1
            conditions.append(f"type = ${param_count}")
            params.append(event_type)

        param_count += 1

        query = f"""
            SELECT 
                e.id,
                e.type,
                e.timestamp,
                e.camera_id,
                c.name as camera_name,
                e.threat_level,
                e.title,
                e.description,
                e.metadata
            FROM timeline_events e
            LEFT JOIN cameras c ON e.camera_id = c.id
            WHERE {' AND '.join(conditions)}
            ORDER BY e.timestamp DESC
            LIMIT ${param_count}
        """

        return await self.fetch_all(query, *params, limit)

    async def create_timeline_event(
        self,
        event_id: str,
        event_type: str,
        camera_id: Optional[str],
        threat_level: Optional[str],
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a timeline event."""
        query = """
            INSERT INTO timeline_events (
                id, type, timestamp, camera_id, threat_level,
                title, description, metadata
            ) VALUES ($1, $2, NOW(), $3, $4, $5, $6, $7)
        """
        await self.execute(
            query,
            event_id,
            event_type,
            camera_id,
            threat_level,
            title,
            description,
            metadata or {}
        )

    async def get_alert_statistics(self, hours: int = 24) -> Dict[str, int]:
        """Get alert statistics for time period."""
        query = f"""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'active') as active,
                COUNT(*) FILTER (WHERE status = 'acknowledged') as acknowledged,
                COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                COUNT(*) FILTER (WHERE priority = 'critical') as critical,
                COUNT(*) FILTER (WHERE priority = 'high') as high,
                COUNT(*) FILTER (WHERE priority = 'medium') as medium,
                COUNT(*) FILTER (WHERE priority = 'low') as low
            FROM alerts
            WHERE timestamp > NOW() - INTERVAL '{hours} hours'
        """
        result = await self.fetch_one(query)
        return result or {}

    async def get_threat_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat statistics for time period."""
        query = f"""
            SELECT 
                COUNT(*) as total_threats,
                AVG(threat_score) as avg_threat_score,
                MAX(threat_score) as max_threat_score,
                COUNT(*) FILTER (WHERE threat_level = 'critical') as critical_threats,
                COUNT(*) FILTER (WHERE threat_level = 'high') as high_threats,
                COUNT(DISTINCT camera_id) as cameras_with_threats
            FROM intelligence_results
            WHERE timestamp > NOW() - INTERVAL '{hours} hours'
            AND threat_score > 0.3
        """
        result = await self.fetch_one(query)
        return result or {}

    async def calculate_threat_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Calculate threat trend compared to previous period."""
        query = f"""
            WITH current_period AS (
                SELECT COUNT(*) as count
                FROM intelligence_results
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                AND threat_score > 0.3
            ),
            previous_period AS (
                SELECT COUNT(*) as count
                FROM intelligence_results
                WHERE timestamp BETWEEN 
                    NOW() - INTERVAL '{hours * 2} hours' 
                    AND NOW() - INTERVAL '{hours} hours'
                AND threat_score > 0.3
            )
            SELECT 
                c.count as current,
                p.count as previous
            FROM current_period c, previous_period p
        """

        result = await self.fetch_one(query)
        if not result:
            return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}

        current = result['current'] or 0
        previous = result['previous'] or 0

        if previous > 0:
            change = ((current - previous) / previous) * 100
        else:
            change = 0

        direction = "up" if change > 5 else "down" if change < -5 else "stable"

        return {
            "current": current,
            "previous": previous,
            "change_percentage": round(abs(change), 1),
            "direction": direction
        }

    async def get_camera_statistics(self) -> Dict[str, int]:
        """Get camera statistics."""
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'online') as online,
                COUNT(*) FILTER (WHERE status = 'offline') as offline,
                COUNT(*) FILTER (WHERE status = 'error') as error,
                COUNT(*) FILTER (WHERE status = 'maintenance') as maintenance
            FROM cameras
        """
        result = await self.fetch_one(query)
        return result or {"total": 0, "online": 0, "offline": 0, "error": 0, "maintenance": 0}

    async def health_check(self) -> bool:
        """
        Perform database health check.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.pool:
                return False

            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        if not self.pool:
            return {"connected": False}

        return {
            "connected": True,
            "size": self.pool.get_size(),
            "free": self.pool.get_idle_size(),
            "min_size": self.pool.get_min_size(),
            "max_size": self.pool.get_max_size(),
        }
