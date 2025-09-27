"""
Alert Manager for AI Security Lab v4.0

Handles alert generation, escalation, and notification management.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertChannel(Enum):
    """Alert notification channels."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    DATABASE = "database"


class Alert:
    """Represents a security alert."""

    def __init__(
        self,
        alert_id: str,
        alert_type: str,
        priority: AlertPriority,
        title: str,
        message: str,
        camera_id: str,
        metadata: Dict[str, Any],
        channels: List[AlertChannel] = None
    ):
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.priority = priority
        self.title = title
        self.message = message
        self.camera_id = camera_id
        self.metadata = metadata
        self.channels = channels or [AlertChannel.DATABASE, AlertChannel.WEBHOOK]
        self.created_at = datetime.utcnow()
        self.acknowledged_at: Optional[datetime] = None
        self.acknowledged_by: Optional[str] = None
        self.resolved_at: Optional[datetime] = None
        self.resolved_by: Optional[str] = None
        self.escalation_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "camera_id": self.camera_id,
            "metadata": self.metadata,
            "channels": [c.value for c in self.channels],
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "escalation_count": self.escalation_count
        }

    def is_acknowledged(self) -> bool:
        """Check if alert is acknowledged."""
        return self.acknowledged_at is not None

    def is_resolved(self) -> bool:
        """Check if alert is resolved."""
        return self.resolved_at is not None

    def should_escalate(self, max_escalations: int = 3) -> bool:
        """Check if alert should be escalated."""
        return (
            not self.is_resolved() and
            self.escalation_count < max_escalations and
            self.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]
        )


class AlertManager:
    """
    Manages security alerts and notifications.
    """

    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.redis_client = None
        self.webhook_url: Optional[str] = None
        self.is_initialized = False

        # Escalation configuration
        self.escalation_rules = {
            AlertPriority.LOW: timedelta(minutes=30),
            AlertPriority.MEDIUM: timedelta(minutes=15),
            AlertPriority.HIGH: timedelta(minutes=5),
            AlertPriority.CRITICAL: timedelta(minutes=2)
        }

    async def initialize(self, webhook_url: Optional[str] = None):
        """Initialize the alert manager."""
        try:
            # Redis connection for caching
            self.redis_client = redis.Redis(
                host="redis-stack",
                port=6379,
                decode_responses=True
            )

            self.webhook_url = webhook_url

            # Load active alerts from Redis
            await self._load_active_alerts()

            self.is_initialized = True
            logger.info("Alert manager initialized")

        except Exception as e:
            logger.error(f"Failed to initialize alert manager: {e}")
            raise

    async def _load_active_alerts(self):
        """Load active alerts from Redis cache."""
        try:
            # Get all active alert keys
            pattern = "alert:active:*"
            keys = await self.redis_client.keys(pattern)

            for key in keys:
                alert_data = await self.redis_client.get(key)
                if alert_data:
                    data = json.loads(alert_data)
                    alert = self._dict_to_alert(data)
                    self.active_alerts[alert.alert_id] = alert

            logger.info(f"Loaded {len(self.active_alerts)} active alerts")

        except Exception as e:
            logger.error(f"Failed to load active alerts: {e}")

    def _dict_to_alert(self, data: Dict[str, Any]) -> Alert:
        """Convert dictionary to Alert object."""
        alert = Alert(
            alert_id=data["alert_id"],
            alert_type=data["alert_type"],
            priority=AlertPriority(data["priority"]),
            title=data["title"],
            message=data["message"],
            camera_id=data["camera_id"],
            metadata=data["metadata"],
            channels=[AlertChannel(c) for c in data["channels"]]
        )

        if data.get("acknowledged_at"):
            alert.acknowledged_at = datetime.fromisoformat(data["acknowledged_at"])
        if data.get("acknowledged_by"):
            alert.acknowledged_by = data["acknowledged_by"]
        if data.get("resolved_at"):
            alert.resolved_at = datetime.fromisoformat(data["resolved_at"])
        if data.get("resolved_by"):
            alert.resolved_by = data["resolved_by"]
        if data.get("escalation_count"):
            alert.escalation_count = data["escalation_count"]

        return alert

    async def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """
        Create a new security alert.

        Args:
            alert_data: Alert information

        Returns:
            Created Alert object
        """
        try:
            alert_id = f"alert_{datetime.utcnow().timestamp()}_{alert_data['camera_id']}"

            # Determine priority from threat score
            threat_score = alert_data.get("threat_score", 0.0)
            if threat_score >= 0.8:
                priority = AlertPriority.CRITICAL
            elif threat_score >= 0.6:
                priority = AlertPriority.HIGH
            elif threat_score >= 0.4:
                priority = AlertPriority.MEDIUM
            else:
                priority = AlertPriority.LOW

            # Create alert
            alert = Alert(
                alert_id=alert_id,
                alert_type=alert_data["type"],
                priority=priority,
                title=self._generate_alert_title(alert_data),
                message=self._generate_alert_message(alert_data),
                camera_id=alert_data["camera_id"],
                metadata=alert_data
            )

            # Store alert
            self.active_alerts[alert_id] = alert

            # Cache in Redis
            await self._cache_alert(alert)

            # Send notifications
            await self._send_alert_notifications(alert)

            logger.info(f"Created alert: {alert_id} (priority: {priority.value})")
            return alert

        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise

    def _generate_alert_title(self, alert_data: Dict[str, Any]) -> str:
        """Generate alert title."""
        alert_type = alert_data.get("type", "unknown")
        camera_id = alert_data.get("camera_id", "unknown")
        threat_level = alert_data.get("level", "unknown")

        return f"Security Alert: {alert_type.title()} - {camera_id} ({threat_level})"

    def _generate_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Generate alert message."""
        alert_type = alert_data.get("type", "unknown")
        camera_id = alert_data.get("camera_id", "unknown")
        threat_score = alert_data.get("threat_score", 0.0)
        primary_threat = alert_data.get("primary_threat", "unknown")

        return (
            f"Alert Type: {alert_type}\n"
            f"Camera: {camera_id}\n"
            f"Threat Score: {threat_score:.3f}\n"
            f"Primary Threat: {primary_threat}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    async def _cache_alert(self, alert: Alert):
        """Cache alert in Redis."""
        try:
            cache_key = f"alert:active:{alert.alert_id}"
            await self.redis_client.setex(
                cache_key,
                timedelta(hours=24),  # Keep for 24 hours
                json.dumps(alert.to_dict(), default=str)
            )

            # Also add to alert list for the camera
            camera_key = f"alerts:camera:{alert.camera_id}"
            await self.redis_client.zadd(
                camera_key,
                {alert.alert_id: alert.created_at.timestamp()}
            )

        except Exception as e:
            logger.error(f"Failed to cache alert: {e}")

    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications via configured channels."""
        try:
            # Webhook notification
            if AlertChannel.WEBHOOK in alert.channels and self.webhook_url:
                await self._send_webhook_notification(alert)

            # Database logging (always enabled)
            if AlertChannel.DATABASE in alert.channels:
                await self._log_to_database(alert)

            # Additional channels can be added here
            # - Email notifications
            # - SMS notifications
            # - Push notifications

        except Exception as e:
            logger.error(f"Failed to send alert notifications: {e}")

    async def _send_webhook_notification(self, alert: Alert):
        """Send alert via webhook."""
        try:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai-security-lab-v4"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert: {alert.alert_id}")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Webhook notification error: {e}")

    async def _log_to_database(self, alert: Alert):
        """Log alert to database."""
        try:
            # This would insert into the alerts table
            # For now, just log the action
            logger.info(f"Alert logged to database: {alert.alert_id}")

        except Exception as e:
            logger.error(f"Database logging failed: {e}")

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert."""
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id

            # Update cache
            await self._cache_alert(alert)

            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    async def resolve_alert(self, alert_id: str, user_id: str, resolution: str = "") -> bool:
        """Resolve an alert."""
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id

            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]

            # Update cache (remove from active)
            await self.redis_client.delete(f"alert:active:{alert_id}")

            logger.info(f"Alert resolved: {alert_id} by {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False

    async def escalate_alert(self, alert_id: str) -> bool:
        """Escalate an alert to higher priority."""
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.escalation_count += 1

            # Increase priority if not already critical
            if alert.priority != AlertPriority.CRITICAL:
                if alert.priority == AlertPriority.HIGH:
                    alert.priority = AlertPriority.CRITICAL
                elif alert.priority == AlertPriority.MEDIUM:
                    alert.priority = AlertPriority.HIGH
                elif alert.priority == AlertPriority.LOW:
                    alert.priority = AlertPriority.MEDIUM

            # Update cache
            await self._cache_alert(alert)

            # Send escalated notification
            await self._send_alert_notifications(alert)

            logger.info(f"Alert escalated: {alert_id} (count: {alert.escalation_count})")
            return True

        except Exception as e:
            logger.error(f"Failed to escalate alert: {e}")
            return False

    async def get_active_alerts(
        self,
        camera_id: Optional[str] = None,
        priority: Optional[AlertPriority] = None
    ) -> List[Alert]:
        """Get active alerts with optional filtering."""
        try:
            alerts = list(self.active_alerts.values())

            if camera_id:
                alerts = [a for a in alerts if a.camera_id == camera_id]

            if priority:
                alerts = [a for a in alerts if a.priority == priority]

            return sorted(alerts, key=lambda a: a.priority.value, reverse=True)

        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    async def get_alert_history(
        self,
        camera_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Alert]:
        """Get alert history."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            history = [
                alert for alert in self.alert_history
                if alert.created_at > since
            ]

            if camera_id:
                history = [a for a in history if a.camera_id == camera_id]

            # Sort by creation time (newest first)
            history.sort(key=lambda a: a.created_at, reverse=True)

            return history[:limit]

        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []

    async def process_escalations(self):
        """Process alert escalations based on time and priority."""
        try:
            current_time = datetime.utcnow()
            alerts_to_escalate = []

            for alert in self.active_alerts.values():
                if alert.should_escalate():
                    # Check if escalation time has passed
                    escalation_due = (
                        alert.created_at +
                        self.escalation_rules.get(alert.priority, timedelta(minutes=30))
                    )

                    if current_time >= escalation_due:
                        alerts_to_escalate.append(alert.alert_id)

            # Escalate alerts
            for alert_id in alerts_to_escalate:
                await self.escalate_alert(alert_id)

        except Exception as e:
            logger.error(f"Failed to process escalations: {e}")

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        try:
            active_alerts = list(self.active_alerts.values())

            stats = {
                "total_active": len(active_alerts),
                "by_priority": {},
                "by_type": {},
                "escalated_count": sum(1 for a in active_alerts if a.escalation_count > 0),
                "unacknowledged_count": sum(1 for a in active_alerts if not a.is_acknowledged()),
                "oldest_alert_age_minutes": 0
            }

            # Count by priority
            for alert in active_alerts:
                priority_str = alert.priority.name
                stats["by_priority"][priority_str] = stats["by_priority"].get(priority_str, 0) + 1

                alert_type = alert.alert_type
                stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1

            # Calculate oldest alert age
            if active_alerts:
                oldest_alert = min(active_alerts, key=lambda a: a.created_at)
                age = datetime.utcnow() - oldest_alert.created_at
                stats["oldest_alert_age_minutes"] = int(age.total_seconds() / 60)

            return stats

        except Exception as e:
            logger.error(f"Failed to get alert stats: {e}")
            return {"error": "Failed to retrieve statistics"}

    async def cleanup_old_alerts(self, max_age_hours: int = 168):  # 1 week default
        """Clean up old alerts from memory and cache."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

            # Remove old alerts from active list
            to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if alert.created_at < cutoff_time:
                    to_remove.append(alert_id)

            for alert_id in to_remove:
                alert = self.active_alerts.pop(alert_id)
                self.alert_history.append(alert)

                # Remove from Redis
                await self.redis_client.delete(f"alert:active:{alert_id}")

            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} old alerts")

        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")

    async def shutdown(self):
        """Shutdown the alert manager."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Alert manager shutdown complete")
        except Exception as e:
            logger.error(f"Error during alert manager shutdown: {e}")
