"""
Behavior Analysis Module for AI Security Lab v4.0

Analyzes human and object behavior patterns for threat detection.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class BehaviorAnalyzer:
    """
    Analyzes behavior patterns for threat detection.
    """

    def __init__(self):
        self.behavior_patterns = {}
        self.historical_data = {}
        self.redis_client = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize the behavior analyzer."""
        try:
            # Redis connection for caching behavior data
            self.redis_client = redis.Redis(
                host="redis-stack",
                port=6379,
                decode_responses=True
            )

            # Load behavior patterns
            await self._load_behavior_patterns()

            self.is_initialized = True
            logger.info("Behavior analyzer initialized")

        except Exception as e:
            logger.error(f"Failed to initialize behavior analyzer: {e}")
            raise

    async def _load_behavior_patterns(self):
        """Load predefined behavior patterns."""
        self.behavior_patterns = {
            "suspicious_wandering": {
                "description": "Person wandering in restricted area",
                "threshold": 0.6,
                "duration": 300,  # 5 minutes
                "factors": ["location", "duration", "pattern"]
            },
            "aggressive_behavior": {
                "description": "Aggressive or threatening behavior",
                "threshold": 0.8,
                "factors": ["speed", "proximity", "gestures"]
            },
            "unauthorized_access": {
                "description": "Attempting to access restricted areas",
                "threshold": 0.7,
                "factors": ["location", "time", "frequency"]
            },
            "crowd_gathering": {
                "description": "Unusual crowd gathering",
                "threshold": 0.5,
                "factors": ["density", "location", "duration"]
            }
        }

        logger.info(f"Loaded {len(self.behavior_patterns)} behavior patterns")

    async def analyze_behavior(
        self,
        camera_id: str,
        object_type: str,
        metadata: Dict[str, Any]
    ) -> float:
        """
        Analyze behavior for threat potential.

        Args:
            camera_id: Camera identifier
            object_type: Type of object (person, vehicle, etc.)
            metadata: Additional context data

        Returns:
            Behavior-based threat score (0.0 to 1.0)
        """
        if not self.is_initialized:
            logger.warning("Behavior analyzer not initialized")
            return 0.3  # Neutral score

        try:
            behavior_score = 0.0

            if object_type == "person":
                behavior_score = await self._analyze_person_behavior(camera_id, metadata)
            elif object_type == "vehicle":
                behavior_score = await self._analyze_vehicle_behavior(camera_id, metadata)
            elif object_type == "group":
                behavior_score = await self._analyze_group_behavior(camera_id, metadata)
            else:
                behavior_score = await self._analyze_generic_behavior(camera_id, metadata)

            return min(behavior_score, 1.0)

        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}")
            return 0.3  # Neutral fallback score

    async def _analyze_person_behavior(self, camera_id: str, metadata: Dict[str, Any]) -> float:
        """Analyze individual person behavior."""
        try:
            score = 0.0
            factors = []

            # Factor 1: Dwell time analysis
            dwell_time = metadata.get("dwell_time", 0)
            if dwell_time > 600:  # More than 10 minutes
                score += 0.3
                factors.append("extended_dwell_time")

            # Factor 2: Movement pattern analysis
            movement_pattern = metadata.get("movement_pattern", "normal")
            if movement_pattern in ["erratic", "suspicious"]:
                score += 0.4
                factors.append("suspicious_movement")

            # Factor 3: Time-based analysis
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:  # Unusual hours
                score += 0.2
                factors.append("unusual_hours")

            # Factor 4: Location-based analysis
            if metadata.get("in_restricted_area"):
                score += 0.3
                factors.append("restricted_area")

            # Factor 5: Historical behavior
            historical_score = await self._get_historical_behavior_score(camera_id, "person")
            score += historical_score * 0.2

            logger.debug(f"Person behavior analysis: {score:.3f} (factors: {factors})")
            return score

        except Exception as e:
            logger.error(f"Person behavior analysis failed: {e}")
            return 0.3

    async def _analyze_vehicle_behavior(self, camera_id: str, metadata: Dict[str, Any]) -> float:
        """Analyze vehicle behavior patterns."""
        try:
            score = 0.0
            factors = []

            # Factor 1: Speed analysis
            speed = metadata.get("speed", 0)
            if speed > 50:  # Excessive speed
                score += 0.4
                factors.append("excessive_speed")
            elif speed < 2 and metadata.get("dwell_time", 0) > 300:
                score += 0.3  # Idling too long
                factors.append("extended_idling")

            # Factor 2: Parking violations
            if metadata.get("parking_violation"):
                score += 0.5
                factors.append("parking_violation")

            # Factor 3: Restricted area access
            if metadata.get("in_restricted_area"):
                score += 0.3
                factors.append("restricted_area")

            # Factor 4: Time-based analysis
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:
                score += 0.1
                factors.append("unusual_hours")

            logger.debug(f"Vehicle behavior analysis: {score:.3f} (factors: {factors})")
            return score

        except Exception as e:
            logger.error(f"Vehicle behavior analysis failed: {e}")
            return 0.2

    async def _analyze_group_behavior(self, camera_id: str, metadata: Dict[str, Any]) -> float:
        """Analyze group/crowd behavior patterns."""
        try:
            score = 0.0
            factors = []

            # Factor 1: Crowd density
            density = metadata.get("crowd_density", 0)
            if density > 0.8:  # High density
                score += 0.4
                factors.append("high_density")

            # Factor 2: Group formation
            group_size = metadata.get("group_size", 1)
            if group_size > 10:  # Large group
                score += 0.3
                factors.append("large_group")

            # Factor 3: Duration analysis
            duration = metadata.get("duration", 0)
            if duration > 900:  # More than 15 minutes
                score += 0.2
                factors.append("extended_duration")

            # Factor 4: Location analysis
            if metadata.get("in_restricted_area"):
                score += 0.3
                factors.append("restricted_area")

            logger.debug(f"Group behavior analysis: {score:.3f} (factors: {factors})")
            return score

        except Exception as e:
            logger.error(f"Group behavior analysis failed: {e}")
            return 0.3

    async def _analyze_generic_behavior(self, camera_id: str, metadata: Dict[str, Any]) -> float:
        """Analyze generic object behavior."""
        try:
            score = 0.0

            # Basic analysis for unknown object types
            if metadata.get("in_restricted_area"):
                score += 0.3

            if metadata.get("unusual_movement"):
                score += 0.2

            return score

        except Exception as e:
            logger.error(f"Generic behavior analysis failed: {e}")
            return 0.1

    async def _get_historical_behavior_score(self, camera_id: str, object_type: str) -> float:
        """Get historical behavior score for location and object type."""
        try:
            # Check Redis cache for historical patterns
            cache_key = f"behavior:history:{camera_id}:{object_type}"

            cached_score = await self.redis_client.get(cache_key)
            if cached_score:
                return float(cached_score)

            # Calculate based on recent incidents
            # This would query the database for historical behavior
            historical_score = 0.0

            # Cache the result
            await self.redis_client.setex(cache_key, 3600, historical_score)  # Cache for 1 hour

            return historical_score

        except Exception as e:
            logger.error(f"Failed to get historical behavior score: {e}")
            return 0.0

    def get_behavior_patterns(self) -> Dict[str, Any]:
        """Get available behavior patterns."""
        return {
            "patterns": list(self.behavior_patterns.keys()),
            "count": len(self.behavior_patterns),
            "initialized": self.is_initialized
        }

    def add_behavior_pattern(
        self,
        pattern_id: str,
        description: str,
        threshold: float,
        factors: List[str]
    ):
        """Add a new behavior pattern."""
        self.behavior_patterns[pattern_id] = {
            "description": description,
            "threshold": threshold,
            "factors": factors
        }
        logger.info(f"Added behavior pattern: {pattern_id}")

    async def track_object_behavior(
        self,
        camera_id: str,
        object_id: str,
        object_type: str,
        position: Dict[str, float],
        timestamp: Optional[datetime] = None
    ):
        """Track object behavior over time."""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()

            # Store behavior data in Redis
            behavior_key = f"behavior:track:{camera_id}:{object_type}:{object_id}"

            behavior_data = {
                "position": position,
                "timestamp": timestamp.isoformat(),
                "camera_id": camera_id,
                "object_type": object_type
            }

            # Store with expiration (keep for 24 hours)
            await self.redis_client.setex(
                behavior_key,
                86400,  # 24 hours
                str(behavior_data)
            )

            # Update location-based statistics
            location_key = f"behavior:location:{camera_id}"
            await self.redis_client.zadd(
                location_key,
                {f"{object_type}:{object_id}": timestamp.timestamp()}
            )

        except Exception as e:
            logger.error(f"Failed to track object behavior: {e}")

    async def get_behavior_insights(self, camera_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get behavior insights for a camera."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            # Get behavior statistics
            insights = {
                "camera_id": camera_id,
                "time_range_hours": hours,
                "total_objects_tracked": 0,
                "suspicious_activities": 0,
                "behavior_patterns": [],
                "risk_areas": []
            }

            # This would query the database for detailed insights
            # For now, return basic structure

            return insights

        except Exception as e:
            logger.error(f"Failed to get behavior insights: {e}")
            return {
                "camera_id": camera_id,
                "error": "Failed to retrieve insights"
            }
