"""
Dashboard API Routes for AI Security Lab v4.0
Provides endpoints for the real-time dashboard UI
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from ..services.database import DatabaseService
from ..services.cache import CacheService
from ..core.enhanced_orchestrator import EnhancedAIOrchestrator

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
        # Mock camera data for now
        # TODO: Integrate with actual camera management system
        cameras = [
            {
                "id": "entrance_01",
                "name": "Main Entrance",
                "location": "Building A - Entrance",
                "status": "online",
                "stream_url": "http://localhost:5000/api/entrance_01/latest.jpg",
                "snapshot_url": "http://localhost:5000/api/entrance_01/latest.jpg",
                "threat_count_24h": 3,
                "uptime_percentage": 99.5,
                "metadata": {
                    "resolution": "1080p",
                    "fps": 30,
                    "codec": "h264"
                }
            },
            {
                "id": "parking_01",
                "name": "Parking Lot",
                "location": "Building A - Parking",
                "status": "online",
                "stream_url": "http://localhost:5000/api/parking_01/latest.jpg",
                "snapshot_url": "http://localhost:5000/api/parking_01/latest.jpg",
                "threat_count_24h": 1,
                "uptime_percentage": 98.2,
                "metadata": {
                    "resolution": "1080p",
                    "fps": 30,
                    "codec": "h264"
                }
            },
            {
                "id": "warehouse_01",
                "name": "Warehouse",
                "location": "Building B - Main Floor",
                "status": "online",
                "stream_url": "http://localhost:5000/api/warehouse_01/latest.jpg",
                "snapshot_url": "http://localhost:5000/api/warehouse_01/latest.jpg",
                "threat_count_24h": 0,
                "uptime_percentage": 100.0,
                "metadata": {
                    "resolution": "4K",
                    "fps": 30,
                    "codec": "h265"
                }
            },
        ]
        
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
        # Mock timeline data for now
        # TODO: Implement actual timeline from database
        events = [
            {
                "id": f"event_{i}",
                "type": "threat" if i % 3 == 0 else "alert" if i % 3 == 1 else "camera",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "camera_id": f"camera_{i % 3 + 1}",
                "camera_name": f"Camera {i % 3 + 1}",
                "threat_level": ["low", "medium", "high"][i % 3],
                "title": f"Event {i}",
                "description": f"Description for event {i}",
                "metadata": {
                    "detection_type": "person",
                    "confidence": 0.85
                }
            }
            for i in range(min(20, hours))
        ]
        
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
        # Mock alert data for now
        # TODO: Implement actual alert retrieval from database
        alerts = [
            {
                "id": "alert_001",
                "camera_id": "entrance_01",
                "camera_name": "Main Entrance",
                "threat_level": "high",
                "priority": "high",
                "message": "Suspicious behavior detected",
                "description": "Person loitering for extended period",
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "status": "active",
                "threat_score": 0.75
            },
            {
                "id": "alert_002",
                "camera_id": "parking_01",
                "camera_name": "Parking Lot",
                "threat_level": "critical",
                "priority": "critical",
                "message": "Weapon detected",
                "description": "Potential firearm identified",
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "status": "active",
                "threat_score": 0.92
            },
        ]
        
        # Apply filters
        if status:
            alerts = [a for a in alerts if a["status"] == status]
        if priority:
            alerts = [a for a in alerts if a["priority"] == priority]
        if camera_id:
            alerts = [a for a in alerts if a["camera_id"] == camera_id]
        
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
        # Mock statistics for now
        # TODO: Implement actual statistics from database
        return {
            "total": 15,
            "active": 5,
            "acknowledged": 7,
            "resolved": 3,
            "critical": 2,
            "high": 5,
            "medium": 6,
            "low": 2
        }
    except Exception as e:
        logger.error(f"Failed to get alert statistics: {e}")
        return {}


async def get_camera_statistics() -> dict:
    """Get camera statistics."""
    try:
        # Mock statistics for now
        # TODO: Implement actual camera statistics
        return {
            "total": 3,
            "online": 3,
            "offline": 0,
            "error": 0,
            "maintenance": 0
        }
    except Exception as e:
        logger.error(f"Failed to get camera statistics: {e}")
        return {"total": 0, "online": 0, "offline": 0, "error": 0, "maintenance": 0}


async def calculate_threat_trend(hours: int = 24) -> dict:
    """Calculate threat trend compared to previous period."""
    try:
        # Mock trend calculation
        # TODO: Implement actual trend calculation from database
        current = 15
        previous = 12
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        
        return {
            "current": current,
            "previous": previous,
            "change_percentage": round(change, 1),
            "direction": "up" if change > 5 else "down" if change < -5 else "stable"
        }
    except Exception as e:
        logger.error(f"Failed to calculate threat trend: {e}")
        return {"current": 0, "previous": 0, "change_percentage": 0, "direction": "stable"}


async def calculate_alert_trend(hours: int = 24) -> dict:
    """Calculate alert trend compared to previous period."""
    try:
        # Mock trend calculation
        # TODO: Implement actual trend calculation from database
        current = 5
        previous = 8
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        
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
