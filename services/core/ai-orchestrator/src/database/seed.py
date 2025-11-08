"""
Database Seed Script for AI Security Lab v4.0
Populates initial data for development and testing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import uuid

from ..services.database import DatabaseService

logger = logging.getLogger(__name__)


async def seed_cameras(db: DatabaseService) -> List[str]:
    """Seed initial camera data."""
    cameras = [
        {
            "id": "entrance_01",
            "name": "Main Entrance",
            "location": "Building A - Main Entrance",
            "status": "online",
            "stream_url": "http://frigate-plus:5000/api/entrance_01/stream",
            "snapshot_url": "http://frigate-plus:5000/api/entrance_01/latest.jpg",
            "uptime_percentage": 99.5,
            "metadata": {
                "resolution": "1080p",
                "fps": 30,
                "codec": "h264",
                "location_type": "entrance",
                "priority": "high"
            }
        },
        {
            "id": "parking_01",
            "name": "Parking Lot North",
            "location": "Building A - North Parking",
            "status": "online",
            "stream_url": "http://frigate-plus:5000/api/parking_01/stream",
            "snapshot_url": "http://frigate-plus:5000/api/parking_01/latest.jpg",
            "uptime_percentage": 98.2,
            "metadata": {
                "resolution": "1080p",
                "fps": 30,
                "codec": "h264",
                "location_type": "parking",
                "priority": "medium"
            }
        },
        {
            "id": "warehouse_01",
            "name": "Warehouse Floor",
            "location": "Building B - Main Floor",
            "status": "online",
            "stream_url": "http://frigate-plus:5000/api/warehouse_01/stream",
            "snapshot_url": "http://frigate-plus:5000/api/warehouse_01/latest.jpg",
            "uptime_percentage": 100.0,
            "metadata": {
                "resolution": "4K",
                "fps": 30,
                "codec": "h265",
                "location_type": "warehouse",
                "priority": "medium"
            }
        },
        {
            "id": "lobby_01",
            "name": "Main Lobby",
            "location": "Building A - Lobby",
            "status": "online",
            "stream_url": "http://frigate-plus:5000/api/lobby_01/stream",
            "snapshot_url": "http://frigate-plus:5000/api/lobby_01/latest.jpg",
            "uptime_percentage": 97.8,
            "metadata": {
                "resolution": "1080p",
                "fps": 30,
                "codec": "h264",
                "location_type": "lobby",
                "priority": "high"
            }
        },
        {
            "id": "back_exit_01",
            "name": "Back Exit",
            "location": "Building A - Back Exit",
            "status": "online",
            "stream_url": "http://frigate-plus:5000/api/back_exit_01/stream",
            "snapshot_url": "http://frigate-plus:5000/api/back_exit_01/latest.jpg",
            "uptime_percentage": 96.5,
            "metadata": {
                "resolution": "720p",
                "fps": 30,
                "codec": "h264",
                "location_type": "exit",
                "priority": "medium"
            }
        },
    ]
    
    query = """
        INSERT INTO cameras (
            id, name, location, status, stream_url, snapshot_url,
            uptime_percentage, metadata, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            location = EXCLUDED.location,
            status = EXCLUDED.status,
            stream_url = EXCLUDED.stream_url,
            snapshot_url = EXCLUDED.snapshot_url,
            uptime_percentage = EXCLUDED.uptime_percentage,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
    """
    
    camera_ids = []
    for camera in cameras:
        await db.execute(
            query,
            camera["id"],
            camera["name"],
            camera["location"],
            camera["status"],
            camera["stream_url"],
            camera["snapshot_url"],
            camera["uptime_percentage"],
            camera["metadata"]
        )
        camera_ids.append(camera["id"])
        logger.info(f"Seeded camera: {camera['name']}")
    
    return camera_ids


async def seed_intelligence_results(db: DatabaseService, camera_ids: List[str]) -> List[str]:
    """Seed sample intelligence results for last 7 days."""
    detection_ids = []
    threat_levels = ['none', 'low', 'medium', 'high', 'critical']
    threat_weights = [0.5, 0.25, 0.15, 0.08, 0.02]  # Probability distribution
    
    # Generate data for last 7 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    
    # Generate 10-20 detections per day per camera
    query = """
        INSERT INTO intelligence_results (
            detection_id, camera_id, timestamp, threat_score,
            threat_level, ai_models_used, insights, processing_time_ms
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """
    
    for camera_id in camera_ids:
        for day in range(7):
            num_detections = random.randint(10, 20)
            
            for _ in range(num_detections):
                # Random timestamp within the day
                day_start = start_time + timedelta(days=day)
                random_seconds = random.randint(0, 86400)
                timestamp = day_start + timedelta(seconds=random_seconds)
                
                # Generate threat data
                threat_level = random.choices(threat_levels, weights=threat_weights)[0]
                
                if threat_level == 'critical':
                    threat_score = random.uniform(0.85, 1.0)
                    primary_threat = random.choice([
                        "Weapon detected",
                        "Aggressive behavior",
                        "Unauthorized access attempt"
                    ])
                elif threat_level == 'high':
                    threat_score = random.uniform(0.7, 0.85)
                    primary_threat = random.choice([
                        "Suspicious behavior",
                        "Loitering detected",
                        "Access violation"
                    ])
                elif threat_level == 'medium':
                    threat_score = random.uniform(0.5, 0.7)
                    primary_threat = random.choice([
                        "Unusual movement pattern",
                        "Extended dwell time",
                        "Policy violation"
                    ])
                elif threat_level == 'low':
                    threat_score = random.uniform(0.3, 0.5)
                    primary_threat = "Minor anomaly detected"
                else:
                    threat_score = random.uniform(0.0, 0.3)
                    primary_threat = "Normal activity"
                
                detection_id = f"det_{uuid.uuid4().hex[:16]}"
                
                insights = {
                    "primary_threat": primary_threat,
                    "detection_type": random.choice(["person", "vehicle", "object"]),
                    "confidence": round(random.uniform(0.7, 0.99), 2),
                    "threat_factors": [
                        {
                            "name": "behavior_analysis",
                            "score": round(threat_score * random.uniform(0.8, 1.2), 2),
                            "description": "Behavioral pattern analysis"
                        }
                    ]
                }
                
                processing_time = random.uniform(50, 150)
                
                await db.execute(
                    query,
                    detection_id,
                    camera_id,
                    timestamp,
                    threat_score,
                    threat_level,
                    ["threat_detector", "behavior_analyzer"],
                    insights,
                    processing_time
                )
                
                detection_ids.append(detection_id)
    
    logger.info(f"Seeded {len(detection_ids)} intelligence results")
    return detection_ids


async def seed_alerts(db: DatabaseService, camera_ids: List[str]) -> List[str]:
    """Seed sample alerts."""
    alert_ids = []
    
    # Create alerts for last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Active alerts (recent)
    active_alerts = [
        {
            "camera_id": "entrance_01",
            "threat_level": "high",
            "priority": "high",
            "message": "Suspicious behavior detected",
            "description": "Person loitering for extended period near entrance",
            "hours_ago": 0.5
        },
        {
            "camera_id": "parking_01",
            "threat_level": "critical",
            "priority": "critical",
            "message": "Potential weapon detected",
            "description": "Object resembling firearm identified in parking area",
            "hours_ago": 1.0
        },
        {
            "camera_id": "warehouse_01",
            "threat_level": "medium",
            "priority": "medium",
            "message": "Unauthorized access attempt",
            "description": "Person attempting to access restricted warehouse area",
            "hours_ago": 2.5
        },
    ]
    
    # Acknowledged alerts
    acknowledged_alerts = [
        {
            "camera_id": "lobby_01",
            "threat_level": "medium",
            "priority": "medium",
            "message": "Crowd gathering detected",
            "description": "Unusual crowd formation in lobby area",
            "hours_ago": 5.0,
            "acknowledged_by": "operator_1"
        },
        {
            "camera_id": "entrance_01",
            "threat_level": "low",
            "priority": "low",
            "message": "Extended dwell time",
            "description": "Person standing near entrance for 10+ minutes",
            "hours_ago": 8.0,
            "acknowledged_by": "operator_2"
        },
    ]
    
    # Resolved alerts
    resolved_alerts = [
        {
            "camera_id": "parking_01",
            "threat_level": "medium",
            "priority": "medium",
            "message": "Vehicle speed violation",
            "description": "Vehicle exceeding speed limit in parking area",
            "hours_ago": 12.0,
            "resolved_by": "admin",
            "resolution_notes": "Driver identified and warned. No further action needed."
        },
        {
            "camera_id": "back_exit_01",
            "threat_level": "low",
            "priority": "low",
            "message": "Door left open",
            "description": "Back exit door detected open after hours",
            "hours_ago": 18.0,
            "resolved_by": "security_guard",
            "resolution_notes": "Door secured. Reminded staff to check exits."
        },
    ]
    
    # Insert active alerts
    for alert_data in active_alerts:
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        timestamp = end_time - timedelta(hours=alert_data["hours_ago"])
        
        query = """
            INSERT INTO alerts (
                id, camera_id, threat_level, priority,
                message, description, timestamp, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')
        """
        
        await db.execute(
            query,
            alert_id,
            alert_data["camera_id"],
            alert_data["threat_level"],
            alert_data["priority"],
            alert_data["message"],
            alert_data["description"],
            timestamp
        )
        alert_ids.append(alert_id)
    
    # Insert acknowledged alerts
    for alert_data in acknowledged_alerts:
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        timestamp = end_time - timedelta(hours=alert_data["hours_ago"])
        ack_time = timestamp + timedelta(minutes=random.randint(5, 30))
        
        query = """
            INSERT INTO alerts (
                id, camera_id, threat_level, priority,
                message, description, timestamp, status,
                acknowledged_by, acknowledged_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'acknowledged', $8, $9)
        """
        
        await db.execute(
            query,
            alert_id,
            alert_data["camera_id"],
            alert_data["threat_level"],
            alert_data["priority"],
            alert_data["message"],
            alert_data["description"],
            timestamp,
            alert_data["acknowledged_by"],
            ack_time
        )
        alert_ids.append(alert_id)
    
    # Insert resolved alerts
    for alert_data in resolved_alerts:
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        timestamp = end_time - timedelta(hours=alert_data["hours_ago"])
        ack_time = timestamp + timedelta(minutes=random.randint(5, 15))
        resolve_time = ack_time + timedelta(minutes=random.randint(10, 60))
        
        query = """
            INSERT INTO alerts (
                id, camera_id, threat_level, priority,
                message, description, timestamp, status,
                acknowledged_by, acknowledged_at,
                resolved_by, resolved_at, resolution_notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'resolved', $8, $9, $10, $11, $12)
        """
        
        await db.execute(
            query,
            alert_id,
            alert_data["camera_id"],
            alert_data["threat_level"],
            alert_data["priority"],
            alert_data["message"],
            alert_data["description"],
            timestamp,
            "operator_1",
            ack_time,
            alert_data["resolved_by"],
            resolve_time,
            alert_data["resolution_notes"]
        )
        alert_ids.append(alert_id)
    
    logger.info(f"Seeded {len(alert_ids)} alerts")
    return alert_ids


async def seed_timeline_events(db: DatabaseService, camera_ids: List[str]) -> List[str]:
    """Seed sample timeline events."""
    event_ids = []
    end_time = datetime.utcnow()
    
    # Create various event types
    events = [
        {
            "type": "system",
            "hours_ago": 0.2,
            "camera_id": None,
            "threat_level": None,
            "title": "System startup",
            "description": "AI Security Lab v4.0 started successfully",
            "metadata": {"version": "4.0.0", "service": "ai_orchestrator"}
        },
        {
            "type": "camera",
            "hours_ago": 1.0,
            "camera_id": "entrance_01",
            "threat_level": None,
            "title": "Camera online",
            "description": "Main Entrance camera came online",
            "metadata": {"previous_status": "offline", "uptime": "99.5%"}
        },
        {
            "type": "threat",
            "hours_ago": 2.5,
            "camera_id": "parking_01",
            "threat_level": "high",
            "title": "High threat detected",
            "description": "Suspicious activity in parking lot",
            "metadata": {"threat_score": 0.82, "primary_threat": "Suspicious behavior"}
        },
        {
            "type": "alert",
            "hours_ago": 5.0,
            "camera_id": "lobby_01",
            "threat_level": "medium",
            "title": "Alert acknowledged",
            "description": "Crowd gathering alert acknowledged by operator",
            "metadata": {"acknowledged_by": "operator_1", "alert_id": "alert_123"}
        },
        {
            "type": "system",
            "hours_ago": 12.0,
            "camera_id": None,
            "threat_level": None,
            "title": "Database backup completed",
            "description": "Automated database backup finished successfully",
            "metadata": {"backup_size_mb": 245, "duration_seconds": 45}
        },
    ]
    
    query = """
        INSERT INTO timeline_events (
            id, type, timestamp, camera_id, threat_level,
            title, description, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """
    
    for event in events:
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        timestamp = end_time - timedelta(hours=event["hours_ago"])
        
        await db.execute(
            query,
            event_id,
            event["type"],
            timestamp,
            event["camera_id"],
            event["threat_level"],
            event["title"],
            event["description"],
            event["metadata"]
        )
        event_ids.append(event_id)
    
    logger.info(f"Seeded {len(event_ids)} timeline events")
    return event_ids


async def seed_users(db: DatabaseService) -> List[str]:
    """Seed default users."""
    users = [
        {
            "id": "user_admin",
            "username": "admin",
            "email": "admin@aisecuritylab.com",
            "password_hash": "$2b$12$placeholder_hash_for_development",  # TODO: Use proper hashing
            "role": "admin"
        },
        {
            "id": "user_operator1",
            "username": "operator_1",
            "email": "operator1@aisecuritylab.com",
            "password_hash": "$2b$12$placeholder_hash_for_development",
            "role": "operator"
        },
        {
            "id": "user_viewer1",
            "username": "viewer_1",
            "email": "viewer1@aisecuritylab.com",
            "password_hash": "$2b$12$placeholder_hash_for_development",
            "role": "viewer"
        },
    ]
    
    query = """
        INSERT INTO users (
            id, username, email, password_hash, role, is_active, created_at
        ) VALUES ($1, $2, $3, $4, $5, TRUE, NOW())
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            role = EXCLUDED.role
    """
    
    user_ids = []
    for user in users:
        await db.execute(
            query,
            user["id"],
            user["username"],
            user["email"],
            user["password_hash"],
            user["role"]
        )
        user_ids.append(user["id"])
        logger.info(f"Seeded user: {user['username']} ({user['role']})")
    
    return user_ids


async def run_seed(db: DatabaseService) -> Dict[str, Any]:
    """
    Run all seed operations.
    
    Args:
        db: DatabaseService instance
        
    Returns:
        Dictionary with seeded entity counts
    """
    try:
        logger.info("Starting database seed...")
        
        # Seed in order (respecting dependencies)
        camera_ids = await seed_cameras(db)
        detection_ids = await seed_intelligence_results(db, camera_ids)
        alert_ids = await seed_alerts(db, camera_ids)
        event_ids = await seed_timeline_events(db, camera_ids)
        user_ids = await seed_users(db)
        
        result = {
            "cameras": len(camera_ids),
            "intelligence_results": len(detection_ids),
            "alerts": len(alert_ids),
            "timeline_events": len(event_ids),
            "users": len(user_ids)
        }
        
        logger.info(f"✅ Database seed completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Database seed failed: {e}")
        raise


# ============================================================================
# CLI Entry Point
# ============================================================================

async def main():
    """Run seed script from command line."""
    from ..config.settings import Settings
    
    settings = Settings()
    
    # Create database service
    db = DatabaseService(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password
    )
    
    try:
        # Connect
        await db.connect()
        
        # Run seed
        result = await run_seed(db)
        
        print("\n" + "="*60)
        print("Database Seed Results:")
        print("="*60)
        for entity, count in result.items():
            print(f"  {entity}: {count}")
        print("="*60 + "\n")
        
    finally:
        # Disconnect
        await db.disconnect()


if __name__ == "__main__":
    # Run seed script
    asyncio.run(main())
