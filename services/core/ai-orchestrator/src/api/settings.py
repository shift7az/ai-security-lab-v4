"""
Settings API Router for AI Security Lab v4.0
Provides endpoints for runtime configuration management
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..services.database import DatabaseService
from ..config.settings import Settings as AppSettings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/settings", tags=["settings"])

# Global references
db_service: Optional[DatabaseService] = None
app_settings: Optional[AppSettings] = None


def set_dependencies(db: DatabaseService, settings: AppSettings):
    """Set global dependencies for the router."""
    global db_service, app_settings
    db_service = db
    app_settings = settings


# ============================================================================
# Settings Metadata (Define all configurable settings)
# ============================================================================

def get_settings_metadata() -> List[Dict[str, Any]]:
    """Get metadata for all configurable settings."""
    return [
        # Database Settings
        {
            "key": "database_host",
            "category": "database",
            "value_type": "string",
            "description": "Hostname or IP of TimescaleDB server",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"pattern": r"^[a-zA-Z0-9\-\.]+$"}
        },
        {
            "key": "database_port",
            "category": "database",
            "value_type": "number",
            "description": "PostgreSQL port number",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 65535}
        },
        {
            "key": "database_name",
            "category": "database",
            "value_type": "string",
            "description": "Database name",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "database_user",
            "category": "database",
            "value_type": "string",
            "description": "Database username",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "database_password",
            "category": "database",
            "value_type": "string",
            "description": "Database password",
            "is_secret": True,
            "is_readonly": False
        },
        {
            "key": "database_min_pool_size",
            "category": "database",
            "value_type": "number",
            "description": "Minimum connection pool size",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 50}
        },
        {
            "key": "database_max_pool_size",
            "category": "database",
            "value_type": "number",
            "description": "Maximum connection pool size",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 5, "max": 100}
        },
        
        # Redis/Cache Settings
        {
            "key": "redis_host",
            "category": "cache",
            "value_type": "string",
            "description": "Redis server hostname",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "redis_port",
            "category": "cache",
            "value_type": "number",
            "description": "Redis port number",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 65535}
        },
        {
            "key": "redis_password",
            "category": "cache",
            "value_type": "string",
            "description": "Redis password (leave empty if no auth)",
            "is_secret": True,
            "is_readonly": False
        },
        {
            "key": "redis_max_connections",
            "category": "cache",
            "value_type": "number",
            "description": "Maximum Redis connections",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 10, "max": 200}
        },
        
        # Service URLs
        {
            "key": "frigate_url",
            "category": "services",
            "value_type": "string",
            "description": "Frigate NVR base URL",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "frigate_api_key",
            "category": "services",
            "value_type": "string",
            "description": "Frigate API key",
            "is_secret": True,
            "is_readonly": False
        },
        {
            "key": "threat_detector_url",
            "category": "services",
            "value_type": "string",
            "description": "Threat Detector service URL",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "threat_detector_enabled",
            "category": "services",
            "value_type": "boolean",
            "description": "Enable threat detection service",
            "is_secret": False,
            "is_readonly": False
        },
        
        # Performance Settings
        {
            "key": "max_concurrent_analyses",
            "category": "performance",
            "value_type": "number",
            "description": "Maximum concurrent threat analyses",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 50}
        },
        {
            "key": "worker_count",
            "category": "performance",
            "value_type": "number",
            "description": "Number of worker processes",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 20}
        },
        {
            "key": "detection_queue_size",
            "category": "performance",
            "value_type": "number",
            "description": "Detection queue buffer size",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 100, "max": 5000}
        },
        {
            "key": "gpu_enabled",
            "category": "performance",
            "value_type": "boolean",
            "description": "Enable GPU acceleration",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "batch_size",
            "category": "performance",
            "value_type": "number",
            "description": "Batch processing size",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"min": 1, "max": 32}
        },
        
        # Feature Flags
        {
            "key": "enable_websocket",
            "category": "features",
            "value_type": "boolean",
            "description": "Enable WebSocket real-time updates",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "enable_batch_processing",
            "category": "features",
            "value_type": "boolean",
            "description": "Enable batch frame processing",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "enable_auto_response",
            "category": "features",
            "value_type": "boolean",
            "description": "Enable automated threat response",
            "is_secret": False,
            "is_readonly": False
        },
        
        # Monitoring Settings
        {
            "key": "log_level",
            "category": "monitoring",
            "value_type": "string",
            "description": "Application log level",
            "is_secret": False,
            "is_readonly": False,
            "validation": {"options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
        },
        {
            "key": "enable_metrics",
            "category": "monitoring",
            "value_type": "boolean",
            "description": "Enable Prometheus metrics",
            "is_secret": False,
            "is_readonly": False
        },
        {
            "key": "enable_tracing",
            "category": "monitoring",
            "value_type": "boolean",
            "description": "Enable distributed tracing",
            "is_secret": False,
            "is_readonly": False
        },
    ]


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/")
async def get_all_settings():
    """Get all system settings."""
    try:
        if not db_service or not app_settings:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        metadata = get_settings_metadata()
        result = []
        
        for meta in metadata:
            key = meta["key"]
            
            # Get current value from app settings
            current_value = getattr(app_settings, key, None)
            
            # Check if overridden in database
            db_setting = await db_service.fetch_one(
                "SELECT * FROM system_settings WHERE key = $1",
                key
            )
            
            setting_data = {
                **meta,
                "current_value": current_value,
                "default_value": current_value,  # From Settings class
                "is_modified": db_setting is not None,
            }
            
            if db_setting:
                setting_data["value"] = db_setting["value"]
                setting_data["modified_by"] = db_setting.get("modified_by")
                setting_data["modified_at"] = db_setting.get("modified_at").isoformat() if db_setting.get("modified_at") else None
            else:
                setting_data["value"] = current_value
            
            # Mask secrets
            if meta["is_secret"] and setting_data["value"]:
                setting_data["value"] = "***HIDDEN***"
                setting_data["current_value"] = "***HIDDEN***"
            
            result.append(setting_data)
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get all setting categories with counts."""
    try:
        metadata = get_settings_metadata()
        
        categories = {}
        for setting in metadata:
            cat = setting["category"]
            if cat not in categories:
                categories[cat] = {
                    "id": cat,
                    "name": cat.title(),
                    "count": 0,
                    "icon": get_category_icon(cat)
                }
            categories[cat]["count"] += 1
        
        return list(categories.values())
    
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key}")
async def get_setting(key: str):
    """Get specific setting by key."""
    try:
        if not db_service or not app_settings:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Check if setting exists in metadata
        metadata = next((m for m in get_settings_metadata() if m["key"] == key), None)
        if not metadata:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        # Get current value
        current_value = getattr(app_settings, key, None)
        
        # Check database override
        db_setting = await db_service.fetch_one(
            "SELECT * FROM system_settings WHERE key = $1",
            key
        )
        
        result = {
            **metadata,
            "current_value": current_value,
            "default_value": current_value,
            "is_modified": db_setting is not None
        }
        
        if db_setting:
            result["value"] = db_setting["value"]
            result["modified_by"] = db_setting.get("modified_by")
            result["modified_at"] = db_setting.get("modified_at").isoformat() if db_setting.get("modified_at") else None
        else:
            result["value"] = current_value
        
        # Mask if secret
        if metadata["is_secret"] and result["value"]:
            result["value"] = "***HIDDEN***"
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get setting {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{key}")
async def update_setting(
    key: str,
    value: Any = Body(...),
    user_id: str = Body(..., embed=True)
):
    """Update a setting value."""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Verify setting exists
        metadata = next((m for m in get_settings_metadata() if m["key"] == key), None)
        if not metadata:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        if metadata["is_readonly"]:
            raise HTTPException(status_code=403, detail="Setting is readonly")
        
        # Validate value
        # TODO: Add proper validation based on metadata["validation"]
        
        # Get old value for history
        old_setting = await db_service.fetch_one(
            "SELECT value FROM system_settings WHERE key = $1",
            key
        )
        old_value = old_setting["value"] if old_setting else None
        
        # Upsert setting
        query = """
            INSERT INTO system_settings (
                key, value, category, description, value_type,
                modified_by, modified_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                modified_by = EXCLUDED.modified_by,
                modified_at = NOW()
        """
        
        await db_service.execute(
            query,
            key,
            value,
            metadata["category"],
            metadata["description"],
            metadata["value_type"],
            user_id
        )
        
        # Record in history
        await db_service.execute(
            """
            INSERT INTO settings_history (setting_key, old_value, new_value, modified_by)
            VALUES ($1, $2, $3, $4)
            """,
            key,
            old_value,
            value,
            user_id
        )
        
        logger.info(f"Setting {key} updated by {user_id}")
        
        return {
            "success": True,
            "key": key,
            "value": value if not metadata["is_secret"] else "***HIDDEN***",
            "modified_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update setting {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk")
async def bulk_update_settings(
    updates: List[Dict[str, Any]] = Body(...),
    user_id: str = Body(..., embed=True)
):
    """Bulk update multiple settings."""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        results = []
        errors = []
        
        for update in updates:
            try:
                key = update.get("key")
                value = update.get("value")
                
                if not key:
                    errors.append({"error": "Missing key", "update": update})
                    continue
                
                # Use the single update endpoint logic
                result = await update_setting(key, value, user_id)
                results.append(result)
                
            except Exception as e:
                errors.append({"key": update.get("key"), "error": str(e)})
        
        return {
            "success": len(errors) == 0,
            "updated": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
    
    except Exception as e:
        logger.error(f"Bulk update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{key}/reset")
async def reset_setting(key: str, user_id: str = Body(..., embed=True)):
    """Reset setting to default value."""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Delete from database (will use default)
        await db_service.execute(
            "DELETE FROM system_settings WHERE key = $1",
            key
        )
        
        # Record in history
        await db_service.execute(
            """
            INSERT INTO settings_history (setting_key, old_value, new_value, modified_by, reason)
            VALUES ($1, NULL, NULL, $2, 'Reset to default')
            """,
            key,
            user_id
        )
        
        logger.info(f"Setting {key} reset to default by {user_id}")
        
        return {
            "success": True,
            "key": key,
            "action": "reset",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to reset setting {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key}/history")
async def get_setting_history(key: str, limit: int = 50):
    """Get change history for a setting."""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        history = await db_service.fetch_all(
            """
            SELECT setting_key, old_value, new_value, modified_by, modified_at, reason
            FROM settings_history
            WHERE setting_key = $1
            ORDER BY modified_at DESC
            LIMIT $2
            """,
            key,
            limit
        )
        
        # Convert datetime to ISO
        for record in history:
            if record.get("modified_at"):
                record["modified_at"] = record["modified_at"].isoformat()
        
        return history
    
    except Exception as e:
        logger.error(f"Failed to get history for {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/metadata")
async def get_settings_schema():
    """Get complete settings schema with metadata."""
    return get_settings_metadata()


# ============================================================================
# Utility Functions
# ============================================================================

def get_category_icon(category: str) -> str:
    """Get icon name for category."""
    icons = {
        "database": "database",
        "cache": "hard-drive",
        "services": "zap",
        "performance": "cpu",
        "features": "toggle-right",
        "monitoring": "activity",
        "security": "shield"
    }
    return icons.get(category, "settings")
