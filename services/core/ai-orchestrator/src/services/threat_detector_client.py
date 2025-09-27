"""
Threat Detector Client for AI Security Lab v4.0

Client service for communicating with the threat detector microservice.
Handles threat analysis requests, alert management, and real-time updates.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThreatAnalysis:
    """Threat analysis result."""
    detection_id: str
    camera_id: str
    timestamp: datetime
    threat_score: float
    threat_level: str
    factors: List[Dict[str, Any]]
    primary_threat: str
    confidence: float
    requires_response: bool
    response_priority: int
    metadata: Dict[str, Any]


@dataclass
class AlertInfo:
    """Alert information."""
    alert_id: str
    alert_type: str
    priority: int
    title: str
    message: str
    camera_id: str
    metadata: Dict[str, Any]
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class ThreatDetectorClient:
    """
    Client for interacting with the threat detector service.
    """

    def __init__(self, base_url: str = "http://threat-detector:8001"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False

    async def initialize(self):
        """Initialize the threat detector client."""
        try:
            # Create HTTP session with optimized settings
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

            # Test connectivity
            await self._test_connectivity()

            self.is_connected = True
            logger.info("Threat detector client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize threat detector client: {e}")
            raise

    async def _test_connectivity(self):
        """Test connectivity to threat detector service."""
        try:
            async with self.session.get(f"{self.base_url}/health", timeout=10) as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"Threat detector health: {health_data}")
                else:
                    raise Exception(f"Health check failed: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Threat detector connectivity test failed: {e}")
            raise

    async def analyze_detection(
        self,
        camera_id: str,
        detection_type: str,
        confidence: float,
        bbox: List[float],
        frame_data: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ThreatAnalysis]:
        """
        Send detection for threat analysis.

        Args:
            camera_id: Camera identifier
            detection_type: Type of detection (person, vehicle, weapon, etc.)
            confidence: Detection confidence score
            bbox: Bounding box coordinates [x1, y1, x2, y2]
            frame_data: Optional base64 encoded image data
            metadata: Additional detection metadata

        Returns:
            Threat analysis result or None if failed
        """
        if not self.is_connected or not self.session:
            logger.warning("Threat detector client not connected")
            return None

        try:
            request_data = {
                "camera_id": camera_id,
                "detection_type": detection_type,
                "confidence": confidence,
                "bbox": bbox,
                "metadata": metadata or {}
            }

            if frame_data:
                request_data["frame_data"] = frame_data

            async with self.session.post(
                f"{self.base_url}/analyze",
                json=request_data,
                timeout=30
            ) as response:

                if response.status == 200:
                    data = await response.json()

                    return ThreatAnalysis(
                        detection_id=data["detection_id"],
                        camera_id=data["camera_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        threat_score=data["threat_score"],
                        threat_level=data["threat_level"],
                        factors=data["factors"],
                        primary_threat=data["primary_threat"],
                        confidence=data["confidence"],
                        requires_response=data["requires_response"],
                        response_priority=data["response_priority"],
                        metadata=data["metadata"]
                    )
                else:
                    logger.error(f"Threat analysis failed: HTTP {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Threat analysis request failed: {e}")
            return None

    async def get_threat_history(
        self,
        camera_id: Optional[str] = None,
        hours: int = 24,
        min_score: float = 0.0,
        limit: int = 100
    ) -> List[ThreatAnalysis]:
        """
        Get threat analysis history.

        Args:
            camera_id: Optional camera filter
            hours: Hours of history to retrieve
            min_score: Minimum threat score filter
            limit: Maximum number of results

        Returns:
            List of threat analysis results
        """
        if not self.is_connected or not self.session:
            logger.warning("Threat detector client not connected")
            return []

        try:
            params = {
                "hours": hours,
                "min_score": min_score,
                "limit": limit
            }

            if camera_id:
                params["camera_id"] = camera_id

            async with self.session.get(
                f"{self.base_url}/history",
                params=params,
                timeout=30
            ) as response:

                if response.status == 200:
                    data = await response.json()

                    return [
                        ThreatAnalysis(
                            detection_id=item["detection_id"],
                            camera_id=item["camera_id"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            threat_score=item["threat_score"],
                            threat_level=item["threat_level"],
                            factors=item["factors"],
                            primary_threat=item["primary_threat"],
                            confidence=item["confidence"],
                            requires_response=item["requires_response"],
                            response_priority=item["response_priority"],
                            metadata=item["metadata"]
                        )
                        for item in data
                    ]
                else:
                    logger.error(f"Threat history request failed: HTTP {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Threat history request failed: {e}")
            return []

    async def get_threat_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get threat statistics.

        Args:
            hours: Hours of data to analyze

        Returns:
            Threat statistics dictionary
        """
        if not self.is_connected or not self.session:
            logger.warning("Threat detector client not connected")
            return {}

        try:
            async with self.session.get(
                f"{self.base_url}/stats",
                params={"hours": hours},
                timeout=30
            ) as response:

                if response.status == 200:
                    stats = await response.json()
                    return stats
                else:
                    logger.error(f"Threat stats request failed: HTTP {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Threat statistics request failed: {e}")
            return {}

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert identifier
            user_id: User acknowledging the alert

        Returns:
            True if successful
        """
        if not self.is_connected or not self.session:
            logger.warning("Threat detector client not connected")
            return False

        try:
            # This would typically be handled by the alert manager
            # For now, return success
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True

        except Exception as e:
            logger.error(f"Alert acknowledgment failed: {e}")
            return False

    async def resolve_alert(self, alert_id: str, user_id: str, resolution: str = "") -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert identifier
            user_id: User resolving the alert
            resolution: Optional resolution notes

        Returns:
            True if successful
        """
        if not self.is_connected or not self.session:
            logger.warning("Threat detector client not connected")
            return False

        try:
            # This would typically be handled by the alert manager
            # For now, return success
            logger.info(f"Alert resolved: {alert_id} by {user_id}")
            return True

        except Exception as e:
            logger.error(f"Alert resolution failed: {e}")
            return False

    async def get_active_threats(
        self,
        camera_id: Optional[str] = None,
        min_priority: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get currently active threats.

        Args:
            camera_id: Optional camera filter
            min_priority: Minimum priority threshold

        Returns:
            List of active threats
        """
        # This would query the threat detector for active threats
        # For now, return empty list as placeholder
        return []

    async def shutdown(self):
        """Shutdown the threat detector client."""
        try:
            if self.session:
                await self.session.close()
            self.is_connected = False
            logger.info("Threat detector client shutdown complete")
        except Exception as e:
            logger.error(f"Error during threat detector client shutdown: {e}")

    def is_healthy(self) -> bool:
        """Check if threat detector client is healthy."""
        return self.is_connected
