"""
AI Security Lab v4.0 - AI Orchestrator Service

This is the central intelligence service that coordinates multiple AI models
for comprehensive security analysis, threat detection, and automated response.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.core.enhanced_orchestrator import EnhancedAIOrchestrator
from src.models.detection import DetectionResult, ThreatLevel
from src.services.frigate_client import FrigateClient
from src.services.database import DatabaseService
from src.services.cache import CacheService
from src.utils.logging_config import setup_logging
from src.config.settings import Settings
from src.api import dashboard


# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="tempo",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Global services
orchestrator: Optional[EnhancedAIOrchestrator] = None
frigate_client: Optional[FrigateClient] = None
db_service: Optional[DatabaseService] = None
cache_service: Optional[CacheService] = None

# Settings
settings = Settings()

# Socket.IO for real-time communication
import socketio
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)


# ============================================================================
# LIFECYCLE MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator, frigate_client, db_service, cache_service

    logger.info("Starting AI Security Lab v4.0 AI Orchestrator...")

    # Initialize services
    try:
        # Database service
        db_service = DatabaseService(
            host="timescaledb",
            port=5432,
            database="security_events",
            user="security",
            password=settings.database_password
        )
        await db_service.connect()
        logger.info("Database service connected")

        # Cache service
        cache_service = CacheService(
            host="redis-stack",
            port=6379,
            password=settings.redis_password,
            db=0
        )
        await cache_service.connect()
        logger.info("Cache service connected")

        # Frigate client
        frigate_client = FrigateClient(
            base_url="http://frigate-plus:5000",
            api_key=settings.frigate_api_key
        )
        logger.info("Frigate client initialized")

        # AI Orchestrator
        orchestrator = EnhancedAIOrchestrator(
            db_service=db_service,
            cache_service=cache_service,
            frigate_client=frigate_client,
            settings=settings
        )
        await orchestrator.initialize()
        logger.info("Enhanced AI Orchestrator initialized")
        
        # Set dependencies for dashboard router
        dashboard.set_dependencies(orchestrator, db_service, cache_service)
        logger.info("Dashboard API router configured")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down AI Orchestrator...")
    try:
        if orchestrator:
            await orchestrator.shutdown()
        if db_service:
            await db_service.disconnect()
        if cache_service:
            await cache_service.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="AI Security Lab v4.0 - AI Orchestrator",
    description="Central intelligence service for multi-model AI surveillance",
    version="4.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include dashboard API router
app.include_router(dashboard.router)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)


# ============================================================================
# DATA MODELS
# ============================================================================

class ProcessFrameRequest(BaseModel):
    """Request model for frame processing."""
    camera_id: str
    frame_data: str  # base64 encoded image
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class ProcessFrameResponse(BaseModel):
    """Response model for frame processing."""
    detection_id: str
    detections: List[DetectionResult]
    threat_score: float
    threat_level: ThreatLevel
    processing_time_ms: float
    ai_models_used: List[str]
    insights: Optional[Dict[str, Any]] = {}


class SystemStatus(BaseModel):
    """System status response."""
    status: str
    version: str
    uptime_seconds: float
    active_cameras: int
    total_detections: int
    threat_level: ThreatLevel
    gpu_utilization: float
    memory_usage: float


# ============================================================================
# WEBSOCKET CONNECTIONS
# ============================================================================

active_connections: List[WebSocket] = []


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()

            # Client can send ping/pong or filter requests
            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("filter:"):
                # Handle filtering requests
                filter_type = data.split(":", 1)[1]
                await websocket.send_text(f"Filter set: {filter_type}")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket connection closed")


async def broadcast_event(event: Dict[str, Any]):
    """Broadcast event to all connected WebSocket clients."""
    if not active_connections:
        return

    message = json.dumps(event, default=str)
    disconnected = []

    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket client: {e}")
            disconnected.append(connection)

    # Remove disconnected clients
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)


# ============================================================================
# API ENDPOINTS
# ============================================================================

# ============================================================================
# SOCKET.IO EVENT HANDLERS
# ============================================================================

@sio.event
async def connect(sid, environ):
    """Handle Socket.IO client connection."""
    logger.info(f"Socket.IO client connected: {sid}")
    await sio.emit('connected', {'message': 'Connected to AI Security Lab'}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle Socket.IO client disconnection."""
    logger.info(f"Socket.IO client disconnected: {sid}")


async def broadcast_threat_detection(threat_data: Dict[str, Any]):
    """Broadcast threat detection to all Socket.IO clients."""
    await sio.emit('threat_detected', threat_data)


async def broadcast_new_alert(alert_data: Dict[str, Any]):
    """Broadcast new alert to all Socket.IO clients."""
    await sio.emit('new_alert', alert_data)


async def broadcast_system_update(system_data: Dict[str, Any]):
    """Broadcast system update to all Socket.IO clients."""
    await sio.emit('system_update', system_data)


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if orchestrator:
        return await orchestrator.get_system_health()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "4.0.0"
    }


@app.get("/status", response_model=SystemStatus)
async def system_status():
    """Get comprehensive system status."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        status = await orchestrator.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")


@app.post("/process-frame", response_model=ProcessFrameResponse)
async def process_frame(request: ProcessFrameRequest, background_tasks: BackgroundTasks):
    """Process a single frame through the AI pipeline."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        # Process frame
        result = await orchestrator.process_frame(
            camera_id=request.camera_id,
            frame_data=request.frame_data,
            timestamp=request.timestamp or datetime.utcnow(),
            metadata=request.metadata
        )

        # Broadcast result to WebSocket clients
        background_tasks.add_task(
            broadcast_event,
            {
                "type": "detection",
                "camera_id": request.camera_id,
                "detection": result.dict(),
                "timestamp": datetime.utcnow()
            }
        )

        return ProcessFrameResponse(**result.dict())

    except Exception as e:
        logger.error(f"Failed to process frame: {e}")
        raise HTTPException(status_code=500, detail=f"Frame processing failed: {str(e)}")


@app.post("/process-batch")
async def process_batch_frames(frames: List[ProcessFrameRequest]):
    """Process multiple frames in batch for efficiency."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        results = []
        for frame in frames:
            result = await orchestrator.process_frame(
                camera_id=frame.camera_id,
                frame_data=frame.frame_data,
                timestamp=frame.timestamp or datetime.utcnow(),
                metadata=frame.metadata
            )
            results.append(result)

        return {
            "batch_size": len(frames),
            "results": [ProcessFrameResponse(**r.dict()).dict() for r in results],
            "processing_time_ms": sum(r.processing_time_ms for r in results)
        }

    except Exception as e:
        logger.error(f"Failed to process batch: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/detections/{camera_id}")
async def get_camera_detections(
    camera_id: str,
    limit: int = 100,
    hours: int = 24
):
    """Get recent detections for a specific camera."""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service not available")

    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        detections = await db_service.get_detections(
            camera_id=camera_id,
            since=since,
            limit=limit
        )

        return {
            "camera_id": camera_id,
            "count": len(detections),
            "detections": detections
        }

    except Exception as e:
        logger.error(f"Failed to get camera detections: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve detections")


@app.get("/threats")
async def get_threats(
    min_score: float = 0.5,
    limit: int = 50,
    hours: int = 24
):
    """Get recent threats above specified score."""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service not available")

    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        threats = await db_service.get_threats(
            min_score=min_score,
            since=since,
            limit=limit
        )

        return {
            "threat_count": len(threats),
            "threats": threats
        }

    except Exception as e:
        logger.error(f"Failed to get threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threats")


@app.get("/analytics/patterns")
async def get_behavior_patterns(hours: int = 168):  # 1 week default
    """Get behavioral pattern analysis."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        patterns = await orchestrator.analyze_behavior_patterns(hours=hours)
        return patterns

    except Exception as e:
        logger.error(f"Failed to get behavior patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patterns")


@app.post("/models/reload")
async def reload_models():
    """Reload AI models (for updates)."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        await orchestrator.reload_models()
        return {"message": "Models reloaded successfully"}

    except Exception as e:
        logger.error(f"Failed to reload models: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload models")


@app.get("/models/info")
async def get_model_info():
    """Get information about loaded AI models."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI Orchestrator not initialized")

    try:
        models = await orchestrator.get_model_info()
        return models

    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model info")


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def periodic_health_check():
    """Periodic health check and maintenance tasks."""
    while True:
        try:
            if orchestrator:
                await orchestrator.perform_maintenance()

            # Broadcast system status every 30 seconds
            if active_connections:
                status = await orchestrator.get_system_status() if orchestrator else {}
                await broadcast_event({
                    "type": "system_status",
                    "status": status,
                    "timestamp": datetime.utcnow()
                })

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        await asyncio.sleep(30)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    # Start background health checks
    asyncio.create_task(periodic_health_check())

    logger.info("AI Security Lab v4.0 AI Orchestrator started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("AI Security Lab v4.0 AI Orchestrator shutting down")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
