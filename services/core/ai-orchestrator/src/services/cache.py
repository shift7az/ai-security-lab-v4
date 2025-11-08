"""
Cache Service for AI Security Lab v4.0
Handles Redis caching operations with async support
"""

import json
import logging
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:
    """
    Async Redis cache service with connection pooling.
    """

    def __init__(
        self,
        host: str,
        port: int,
        password: Optional[str] = None,
        db: int = 0,
        max_connections: int = 50,
        decode_responses: bool = True
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.decode_responses = decode_responses

        self.client: Optional[Redis] = None
        self._is_connected = False

    async def connect(self) -> None:
        """
        Establish Redis connection.
        """
        try:
            logger.info(f"Connecting to Redis: {self.host}:{self.port}")

            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=self.decode_responses,
                max_connections=self.max_connections,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )

            # Test connection
            await self.client.ping()

            self._is_connected = True
            logger.info("✅ Redis connection established")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Close Redis connection.
        """
        try:
            if self.client:
                await self.client.close()
                self._is_connected = False
                logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._is_connected and self.client is not None

    # ========================================================================
    # Basic Operations
    # ========================================================================

    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.
        
        Args:
            key: Cache key
            
        Returns:
            Value as string or None
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            if ttl:
                return await self.client.setex(key, ttl, value)
            else:
                return await self.client.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to check key existence {key}: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on key.
        
        Args:
            key: Cache key
            seconds: Seconds until expiration
            
        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Failed to set expiration on {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get remaining TTL for key.
        
        Args:
            key: Cache key
            
        Returns:
            Seconds remaining or -1 if no expiration, -2 if key doesn't exist
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for {key}: {e}")
            return -2

    # ========================================================================
    # JSON Operations
    # ========================================================================

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value by key.
        
        Args:
            key: Cache key
            
        Returns:
            Deserialized JSON object or None
        """
        value = await self.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for key {key}: {e}")
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set JSON value with optional TTL.
        
        Args:
            key: Cache key
            value: Object to serialize
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            serialized = json.dumps(value)
            return await self.set(key, serialized, ttl)
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Failed to serialize JSON for key {key}: {e}")
            return False

    # ========================================================================
    # Hash Operations
    # ========================================================================

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.hget(key, field)
        except Exception as e:
            logger.error(f"Failed to hget {key}.{field}: {e}")
            return None

    async def hset(self, key: str, field: str, value: str) -> bool:
        """Set hash field value."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            await self.client.hset(key, field, value)
            return True
        except Exception as e:
            logger.error(f"Failed to hset {key}.{field}: {e}")
            return False

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Failed to hgetall {key}: {e}")
            return {}

    # ========================================================================
    # List Operations
    # ========================================================================

    async def lpush(self, key: str, *values: str) -> int:
        """Push values to left of list."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Failed to lpush to {key}: {e}")
            return 0

    async def rpush(self, key: str, *values: str) -> int:
        """Push values to right of list."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Failed to rpush to {key}: {e}")
            return 0

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get list range."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Failed to lrange {key}: {e}")
            return []

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim list to specified range."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            await self.client.ltrim(key, start, end)
            return True
        except Exception as e:
            logger.error(f"Failed to ltrim {key}: {e}")
            return False

    # ========================================================================
    # Set Operations
    # ========================================================================

    async def sadd(self, key: str, *members: str) -> int:
        """Add members to set."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.sadd(key, *members)
        except Exception as e:
            logger.error(f"Failed to sadd to {key}: {e}")
            return 0

    async def smembers(self, key: str) -> set:
        """Get all set members."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.smembers(key)
        except Exception as e:
            logger.error(f"Failed to smembers {key}: {e}")
            return set()

    async def sismember(self, key: str, member: str) -> bool:
        """Check if member in set."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.sismember(key, member)
        except Exception as e:
            logger.error(f"Failed to sismember {key}: {e}")
            return False

    # ========================================================================
    # Sorted Set Operations
    # ========================================================================

    async def zadd(
        self,
        key: str,
        mapping: Dict[str, float],
        nx: bool = False,
        xx: bool = False
    ) -> int:
        """Add members to sorted set with scores."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.zadd(key, mapping, nx=nx, xx=xx)
        except Exception as e:
            logger.error(f"Failed to zadd to {key}: {e}")
            return 0

    async def zrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False
    ) -> List:
        """Get sorted set range."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Failed to zrange {key}: {e}")
            return []

    # ========================================================================
    # Pub/Sub Operations
    # ========================================================================

    async def publish(self, channel: str, message: str) -> int:
        """
        Publish message to channel.
        
        Args:
            channel: Channel name
            message: Message to publish
            
        Returns:
            Number of subscribers that received the message
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return 0

    # ========================================================================
    # Utility Methods
    # ========================================================================

    async def flushdb(self) -> bool:
        """
        Clear all keys in current database.
        WARNING: Use with caution!
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            await self.client.flushdb()
            logger.warning("Redis database flushed")
            return True
        except Exception as e:
            logger.error(f"Failed to flush database: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern.
        WARNING: Can be slow on large datasets.
        """
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Perform Redis health check.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.client:
                return False

            result = await self.client.ping()
            return result is True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.info()
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}

    async def dbsize(self) -> int:
        """Get number of keys in database."""
        if not self.client:
            raise RuntimeError("Redis not connected")

        try:
            return await self.client.dbsize()
        except Exception as e:
            logger.error(f"Failed to get dbsize: {e}")
            return 0
