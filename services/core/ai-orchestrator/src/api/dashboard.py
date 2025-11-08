"""
Dashboard API Routes for AI Security Lab v4.0
Provides endpoints for the real-time dashboard UI
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query

from ..core.enhanced_orchestrator import EnhancedAIOrchestrator
from ..services.cache import CacheService
from ..services.database import DatabaseService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Global references (will be injected)
orchestrator: Optional[EnhancedAIOrchestrator] = None
db_service: Optional[DatabaseService] = None
cache_service: Optional[CacheService] = None


def set_dependencies(
    orch: EnhancedAIOrchestrator,
    db: DatabaseService,
    cache: CacheService
):
    """Set global dependencies for the router."""
    global orchestrator, db_service, cache_service
    orchestrator = orch
    db_service = db
    cache_service = cache


# ============================================================================
# Dashboard Overview Endpoints
# ============================================================================

@router.get("/overview")
async def get_dashboard_overview():
    """
    Get aggregate dashboard statistics.
    
    Returns summary of threats, alerts, cameras, and system health.
    """
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Get intelligence summary
        summary = await orchestrator.get_intelligence_summary(hours=24)

        # Get alert statistics
        alert_stats = await get_alert_statistics(hours=24)

        # Get camera statistics
        camera_stats = await get_camera_statistics()

        # Get system health
        health = await orchestrator.get_system_health()

        # Calculate trends (compare to previous 24h)
        threat_trend = await calculate_threat_trend(hours=24)
        alert_trend = await calculate_alert_trend(hours=24)

        return {
            "total_threats": summary.get("threat_statistics", {}).get("total_threats", 0),
            "critical_alerts": alert_stats.get("critical", 0),
            "active_cameras": camera_stats.get("online", 0),
            "total_cameras": camera_stats.get("total", 0),
            "system_health": get_health_percentage(health),
            "health_status": health.get("status", "unknown"),
            "threat_trend": threat_trend,
            "alert_trend": alert_trend,
            "processing_stats": summary.get("processing_statistics", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras")
async def get_cameras():
    """
    Get all cameras with status and recent threat data.
    
    Returns list of cameras with their current status and threat counts.
    """
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Database service not available")

        # Get cameras from database
        cameras = await db_service.get_cameras()

        # Enrich with threat counts
        for camera in cameras:
            threat_count = await db_service.get_camera_threat_count(camera['id'], hours=24)
            camera['threat_count_24h'] = threat_count

        return cameras

    except Exception as e:
        logger.error(f"Failed to get cameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras/{camera_id}")
async def get_camera(camera_id: str):
    """Get specific camera details."""
    try:
        cameras = await get_cameras()
        camera = next((c for c in cameras if c["id"] == camera_id), None)

        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        return camera

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Threat Detection Endpoints
# ============================================================================

@router.get("/threats/recent")
async def get_recent_threats(hours: int = Query(24, ge=1, le=168)):
    """
    Get recent threat detections.
    
    Args:
        hours: Number of hours to look back (1-168)
    
    Returns list of threat detections with analysis.
    """
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Database service not available")

        since = datetime.utcnow() - timedelta(hours=hours)

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
            AND threat_score > 0.3
            ORDER BY timestamp DESC
            LIMIT 100
        """

        results = await db_service.fetch_all(query, since)

        return [{
            "detection_id": r["detection_id"],
            "camera_id": r["camera_id"],
            "threat_score": float(r["threat_score"]),
            "threat_level": r["threat_level"],
            "timestamp": r["timestamp"].isoformat(),
            "primary_threat": r.get("insights", {}).get("primary_threat", "Unknown"),
            "factors_count": len(r.get("insights", {}).get("threat_factors", []))
        } for r in results]

    except Exception as e:
        logger.error(f"Failed to get recent threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence")
async def get_intelligence_results(
    camera_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get intelligence analysis results."""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not initialized")

        if camera_id:
            return await orchestrator.get_camera_intelligence(camera_id, hours)
        else:
            return await orchestrator.get_intelligence_summary(hours)

    except Exception as e:
        logger.error(f"Failed to get intelligence results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_timeline_events(hours: int = Query(24, ge=1, le=168)):
    """
    Get timeline of events for intelligence feed.
    
    Returns chronological list of threats, alerts, and system events.
    """
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Database service not available")

        # Get events from database
        events = await db_service.get_timeline_events(hours=hours, limit=100)

        # Convert datetime to ISO string
        for event in events:
            event['timestamp'] = event['timestamp'].isoformat()

        return events

    except Exception as e:
        logger.error(f"Failed to get timeline events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Alert Management Endpoints
# ============================================================================

@router.get("/alerts/active")
async def get_active_alerts(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    camera_id: Optional[str] = None
):
    """
    Get active alerts with optional filtering.
    
    Query parameters:
        status: Filter by status (active/acknowledged/resolved)
        priority: Filter by priority (low/medium/high/critical)
        camera_id: Filter by camera
    """
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Database service not available")

        # Get alerts from database with filtering
        alerts = await db_service.get_alerts(
            status=status,
            priority=priority,
            camera_id=camera_id,
            limit=100
        )

        # Convert datetime objects to ISO strings
        for alert in alerts:
            alert['timestamp'] = alert['timestamp'].isoformat()
            if alert.get('acknowledged_at'):
                alert['acknowledged_at'] = alert['acknowledged_at'].isoformat()
            if alert.get('resolved_at'):
                alert['resolved_at'] = alert['resolved_at'].isoformat()

        return alerts

    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user_id: str = Body(..., embed=True)):
    """Acknowledge an alert."""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not initialized")

        success = await orchestrator.handle_alert_action(alert_id, "acknowledge", user_id)

        return {
            "success": success,
            "alert_id": alert_id,
            "action": "acknowledged",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    user_id: str = Body(..., embed=True),
    notes: str = Body("", embed=True)
):
    """Resolve an alert with optional notes."""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not initialized")

        success = await orchestrator.handle_alert_action(alert_id, "resolve", user_id, notes)

        return {
            "success": success,
            "alert_id": alert_id,
            "action": "resolved",
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Utility Functions
# ============================================================================

async def get_alert_statistics(hours: int = 24) -> dict:
    """Get alert statistics for the specified time period."""
    try:
        if not db_service:
            return {}

        return await db_service.get_alert_statistics(hours=hours)
    except Exception as e:
        logger.error(f"Failed to get alert statistics: {e}")
        return {}


async def get_camera_statistics() -> dict:
    """Get camera statistics."""
    try:
        if not db_service:
            return {"total": 0, "online": 0, "offline": 0, "error": 0, "maintenance": 0}

        return await db_service.get_camera_statistics()
    except Exception as e:
        logger.error(f"Failed to get camera statistics: {e}")
        return {"total": 0, "online": 0, "offline": 0, "error": 0, "maintenance": 0}


async def calculate_threat_trend(hours: int = 24) -> dict:
    """Calculate threat trend compared to previous period."""
    try:
        if not db_service:
            return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}

        return await db_service.calculate_threat_trend(hours=hours)
    except Exception as e:
        logger.error(f"Failed to calculate threat trend: {e}")
        return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}


async def calculate_alert_trend(hours: int = 24) -> dict:
    """Calculate alert trend compared to previous period."""
    try:
        if not db_service:
            return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}

        # Use similar logic to threat trend but for alerts
        stats_current = await db_service.get_alert_statistics(hours=hours)
        stats_previous = await db_service.get_alert_statistics(hours=hours * 2)

        current = stats_current.get('total', 0)
        # Calculate previous period (subtract current from 2x period)
        previous = stats_previous.get('total', 0) - current

        if previous > 0:
            change = ((current - previous) / previous) * 100
        else:
            change = 0

        return {
            "current": current,
            "previous": previous,
            "change_percentage": round(abs(change), 1),
            "direction": "up" if change > 5 else "down" if change < -5 else "stable"
        }
    except Exception as e:
        logger.error(f"Failed to calculate alert trend: {e}")
        return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}


def get_health_percentage(health: dict) -> int:
    """Calculate overall health percentage from component statuses."""
    try:
        components = health.get("components", {})
        if not components:
            return 0

        healthy_count = sum(1 for status in components.values() if status)
        total_count = len(components)

        return round((healthy_count / total_count) * 100) if total_count > 0 else 0
    except Exception as e:
        logger.error(f"Failed to calculate health percentage: {e}")
        return 0
