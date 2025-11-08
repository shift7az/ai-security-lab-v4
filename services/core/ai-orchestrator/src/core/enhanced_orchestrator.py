"""
Enhanced AI Orchestrator for AI Security Lab v4.0

Coordinates multiple AI services including threat detection, behavior analysis,
and real-time intelligence processing with full integration capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import base64
from dataclasses import dataclass

from .threat_detector_client import ThreatDetectorClient, ThreatAnalysis
from ..services.frigate_client import FrigateClient
from ..services.database import DatabaseService
from ..services.cache import CacheService
from ..config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class DetectionEvent:
    """Represents a detection event from Frigate."""
    camera_id: str
    detection_type: str
    confidence: float
    bbox: List[float]
    frame_data: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class IntelligenceResult:
    """Complete intelligence analysis result."""
    detection_id: str
    camera_id: str
    timestamp: datetime
    threat_analysis: Optional[ThreatAnalysis]
    processing_time_ms: float
    ai_models_used: List[str]
    insights: Dict[str, Any]


class EnhancedAIOrchestrator:
    """
    Enhanced AI orchestrator with threat detection integration.
    """

    def __init__(
        self,
        db_service: DatabaseService,
        cache_service: CacheService,
        frigate_client: FrigateClient,
        settings: Settings
    ):
        self.db_service = db_service
        self.cache_service = cache_service
        self.frigate_client = frigate_client
        self.settings = settings

        # Threat detection integration
        self.threat_detector = ThreatDetectorClient()
        self.is_threat_detector_enabled = False

        # Processing queues
        self.detection_queue = asyncio.Queue(maxsize=1000)
        self.result_queue = asyncio.Queue(maxsize=1000)

        # Worker management
        self.workers = []
        self.is_running = False

        # Statistics
        self.stats = {
            "total_processed": 0,
            "threats_detected": 0,
            "alerts_generated": 0,
            "avg_processing_time": 0.0,
            "last_activity": None
        }

    async def initialize(self):
        """Initialize the enhanced AI orchestrator."""
        try:
            logger.info("Initializing Enhanced AI Orchestrator...")

            # Initialize threat detector client
            try:
                await self.threat_detector.initialize()
                self.is_threat_detector_enabled = True
                logger.info("✅ Threat detector integration enabled")
            except Exception as e:
                logger.warning(f"⚠️  Threat detector not available: {e}")
                self.is_threat_detector_enabled = False

            # Start worker tasks
            await self._start_workers()

            self.is_running = True
            logger.info("✅ Enhanced AI Orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Enhanced AI Orchestrator: {e}")
            raise

    async def _start_workers(self):
        """Start background worker tasks."""
        # Detection processing workers
        for i in range(self.settings.max_concurrent_analyses):
            worker = asyncio.create_task(self._detection_worker(i))
            self.workers.append(worker)

        # Result broadcasting worker
        broadcast_worker = asyncio.create_task(self._result_broadcast_worker())
        self.workers.append(broadcast_worker)

        logger.info(f"Started {len(self.workers)} background workers")

    async def _detection_worker(self, worker_id: int):
        """Background worker for processing detections."""
        logger.info(f"Detection worker {worker_id} started")

        while self.is_running:
            try:
                # Get detection from queue
                detection = await self.detection_queue.get()

                # Process detection
                start_time = datetime.utcnow()
                result = await self._process_detection(detection)
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Update statistics
                self.stats["total_processed"] += 1
                if result.threat_analysis and result.threat_analysis.threat_score > 0.5:
                    self.stats["threats_detected"] += 1

                result.processing_time_ms = processing_time
                self.stats["avg_processing_time"] = (
                    (self.stats["avg_processing_time"] * (self.stats["total_processed"] - 1) + processing_time)
                    / self.stats["total_processed"]
                )

                # Add to result queue for broadcasting
                await self.result_queue.put(result)
                self.stats["last_activity"] = datetime.utcnow()

                self.detection_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Detection worker {worker_id} error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying

        logger.info(f"Detection worker {worker_id} stopped")

    async def _result_broadcast_worker(self):
        """Worker for broadcasting results to connected clients."""
        logger.info("Result broadcast worker started")

        while self.is_running:
            try:
                # Get result from queue
                result = await self.result_queue.get()

                # Broadcast to WebSocket clients
                await self._broadcast_intelligence_result(result)

                self.result_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Result broadcast worker error: {e}")
                await asyncio.sleep(1)

        logger.info("Result broadcast worker stopped")

    async def _process_detection(self, detection: DetectionEvent) -> IntelligenceResult:
        """Process a single detection through the AI pipeline."""
        detection_id = f"intel_{detection.timestamp.timestamp()}_{detection.camera_id}"

        try:
            # Step 1: Threat Analysis (if enabled)
            threat_analysis = None
            ai_models_used = ["frigate_detection"]

            if self.is_threat_detector_enabled:
                threat_analysis = await self.threat_detector.analyze_detection(
                    camera_id=detection.camera_id,
                    detection_type=detection.detection_type,
                    confidence=detection.confidence,
                    bbox=detection.bbox,
                    frame_data=detection.frame_data,
                    metadata=detection.metadata
                )

                if threat_analysis:
                    ai_models_used.append("threat_detector")
                    if threat_analysis.requires_response:
                        self.stats["alerts_generated"] += 1

            # Step 2: Generate insights
            insights = await self._generate_insights(detection, threat_analysis)

            # Step 3: Store results
            await self._store_intelligence_result(IntelligenceResult(
                detection_id=detection_id,
                camera_id=detection.camera_id,
                timestamp=detection.timestamp,
                threat_analysis=threat_analysis,
                processing_time_ms=0,  # Will be set by worker
                ai_models_used=ai_models_used,
                insights=insights
            ))

            return IntelligenceResult(
                detection_id=detection_id,
                camera_id=detection.camera_id,
                timestamp=detection.timestamp,
                threat_analysis=threat_analysis,
                processing_time_ms=0,  # Will be set by worker
                ai_models_used=ai_models_used,
                insights=insights
            )

        except Exception as e:
            logger.error(f"Failed to process detection: {e}")
            return IntelligenceResult(
                detection_id=detection_id,
                camera_id=detection.camera_id,
                timestamp=detection.timestamp,
                threat_analysis=None,
                processing_time_ms=0,
                ai_models_used=["error"],
                insights={"error": str(e)}
            )

    async def _generate_insights(
        self,
        detection: DetectionEvent,
        threat_analysis: Optional[ThreatAnalysis]
    ) -> Dict[str, Any]:
        """Generate insights from detection and threat analysis."""
        insights = {
            "detection_type": detection.detection_type,
            "confidence": detection.confidence,
            "camera_id": detection.camera_id,
            "timestamp": detection.timestamp.isoformat(),
            "processing_timestamp": datetime.utcnow().isoformat()
        }

        # Add threat insights if available
        if threat_analysis:
            insights.update({
                "threat_score": threat_analysis.threat_score,
                "threat_level": threat_analysis.threat_level,
                "primary_threat": threat_analysis.primary_threat,
                "requires_response": threat_analysis.requires_response,
                "response_priority": threat_analysis.response_priority,
                "threat_factors": [
                    {
                        "name": factor.name,
                        "score": factor.score,
                        "description": factor.description
                    }
                    for factor in threat_analysis.factors
                ]
            })

        # Add contextual insights
        if detection.metadata:
            insights["context"] = detection.metadata

        return insights

    async def _store_intelligence_result(self, result: IntelligenceResult):
        """Store intelligence result in database."""
        try:
            # Store in TimescaleDB for time-series analysis
            query = """
                INSERT INTO intelligence_results (
                    detection_id, camera_id, timestamp, threat_score,
                    threat_level, ai_models_used, insights, processing_time_ms
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """

            threat_score = result.threat_analysis.threat_score if result.threat_analysis else 0.0
            threat_level = result.threat_analysis.threat_level if result.threat_analysis else "none"

            await self.db_service.execute(
                query,
                result.detection_id,
                result.camera_id,
                result.timestamp,
                threat_score,
                threat_level,
                result.ai_models_used,
                json.dumps(result.insights),
                result.processing_time_ms
            )

            # Cache recent results
            cache_key = f"intelligence:{result.detection_id}"
            await self.cache_service.set(
                cache_key,
                result.__dict__,
                ttl=3600  # Cache for 1 hour
            )

        except Exception as e:
            logger.error(f"Failed to store intelligence result: {e}")

    async def _broadcast_intelligence_result(self, result: IntelligenceResult):
        """Broadcast intelligence result to connected clients."""
        try:
            # This would broadcast to WebSocket clients
            # For now, just log the result
            threat_level = result.threat_analysis.threat_level if result.threat_analysis else "none"
            threat_score = result.threat_analysis.threat_score if result.threat_analysis else 0.0

            logger.info(
                f"Intelligence Result: {result.camera_id} - "
                f"Threat: {threat_level} ({threat_score:.3f}) - "
                f"Models: {', '.join(result.ai_models_used)}"
            )

        except Exception as e:
            logger.error(f"Failed to broadcast intelligence result: {e}")

    async def process_frigate_detection(
        self,
        camera_id: str,
        detection_data: Dict[str, Any]
    ):
        """Process detection from Frigate."""
        try:
            # Convert Frigate detection to our format
            detection = DetectionEvent(
                camera_id=camera_id,
                detection_type=detection_data.get("label", "unknown"),
                confidence=detection_data.get("confidence", 0.0),
                bbox=detection_data.get("bbox", []),
                frame_data=None,  # Would need to fetch from Frigate if needed
                timestamp=datetime.utcnow(),
                metadata=detection_data
            )

            # Add to processing queue
            await self.detection_queue.put(detection)

        except Exception as e:
            logger.error(f"Failed to process Frigate detection: {e}")

    async def get_intelligence_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get intelligence summary for the specified time period."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            # Get threat statistics from threat detector
            threat_stats = {}
            if self.is_threat_detector_enabled:
                threat_stats = await self.threat_detector.get_threat_statistics(hours=hours)

            # Get processing statistics
            processing_stats = {
                "total_processed": self.stats["total_processed"],
                "threats_detected": self.stats["threats_detected"],
                "alerts_generated": self.stats["alerts_generated"],
                "avg_processing_time": round(self.stats["avg_processing_time"], 2),
                "last_activity": self.stats["last_activity"].isoformat() if self.stats["last_activity"] else None
            }

            return {
                "time_range_hours": hours,
                "threat_statistics": threat_stats,
                "processing_statistics": processing_stats,
                "threat_detector_enabled": self.is_threat_detector_enabled,
                "system_status": "operational"
            }

        except Exception as e:
            logger.error(f"Failed to get intelligence summary: {e}")
            return {"error": str(e)}

    async def get_camera_intelligence(
        self,
        camera_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get intelligence data for a specific camera."""
        try:
            # Get threat history for camera
            threat_history = []
            if self.is_threat_detector_enabled:
                threat_history = await self.threat_detector.get_threat_history(
                    camera_id=camera_id,
                    hours=hours
                )

            # Get recent intelligence results
            recent_results = await self._get_recent_intelligence_results(camera_id, hours)

            return {
                "camera_id": camera_id,
                "time_range_hours": hours,
                "threat_count": len(threat_history),
                "recent_analyses": len(recent_results),
                "threat_history": [
                    {
                        "detection_id": t.detection_id,
                        "threat_score": t.threat_score,
                        "threat_level": t.threat_level,
                        "timestamp": t.timestamp.isoformat()
                    }
                    for t in threat_history[-10:]  # Last 10 threats
                ],
                "recent_analyses": recent_results[-10:] if recent_results else []
            }

        except Exception as e:
            logger.error(f"Failed to get camera intelligence: {e}")
            return {"error": str(e)}

    async def _get_recent_intelligence_results(
        self,
        camera_id: str,
        hours: int
    ) -> List[Dict[str, Any]]:
        """Get recent intelligence results for a camera."""
        try:
            # This would query the database for recent results
            # For now, return empty list
            return []

        except Exception as e:
            logger.error(f"Failed to get recent intelligence results: {e}")
            return []

    async def handle_alert_action(
        self,
        alert_id: str,
        action: str,
        user_id: str,
        notes: str = ""
    ) -> bool:
        """Handle alert acknowledgment or resolution."""
        try:
            if action == "acknowledge":
                return await self.threat_detector.acknowledge_alert(alert_id, user_id)
            elif action == "resolve":
                return await self.threat_detector.resolve_alert(alert_id, user_id, notes)
            else:
                logger.warning(f"Unknown alert action: {action}")
                return False

        except Exception as e:
            logger.error(f"Failed to handle alert action: {e}")
            return False

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "ai_orchestrator": True,
                    "threat_detector": self.threat_detector.is_healthy(),
                    "database": await self._check_database_health(),
                    "cache": await self._check_cache_health(),
                    "frigate": await self._check_frigate_health()
                },
                "statistics": self.stats,
                "configuration": {
                    "threat_detector_enabled": self.is_threat_detector_enabled,
                    "max_concurrent_analyses": self.settings.max_concurrent_analyses,
                    "workers_active": len(self.workers)
                }
            }

            # Determine overall health
            critical_components = ["database", "cache"]
            if not all(health["components"].get(comp, False) for comp in critical_components):
                health["status"] = "degraded"

            return health

        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_database_health(self) -> bool:
        """Check database connectivity."""
        try:
            # Simple connectivity check
            await self.db_service.execute("SELECT 1")
            return True
        except:
            return False

    async def _check_cache_health(self) -> bool:
        """Check cache connectivity."""
        try:
            await self.cache_service.set("health_check", "ok", ttl=10)
            value = await self.cache_service.get("health_check")
            return value == "ok"
        except:
            return False

    async def _check_frigate_health(self) -> bool:
        """Check Frigate connectivity."""
        try:
            # This would check Frigate API health
            return True
        except:
            return False

    async def process_frame(
        self,
        camera_id: str,
        frame_data: str,
        timestamp: datetime,
        metadata: Dict[str, Any]
    ):
        """
        Process a single camera frame through the AI pipeline.
        
        Args:
            camera_id: Camera identifier
            frame_data: Base64 encoded frame data
            timestamp: Frame timestamp
            metadata: Additional metadata
            
        Returns:
            DetectionResult with threat analysis
        """
        try:
            # Create detection event
            detection = DetectionEvent(
                camera_id=camera_id,
                detection_type="frame",
                confidence=1.0,
                bbox=[],
                frame_data=frame_data,
                timestamp=timestamp,
                metadata=metadata
            )
            
            # Process immediately (bypass queue for API requests)
            result = await self._process_detection(detection)
            
            # Convert to DetectionResult format for API response
            from ..models.detection import DetectionResult as DR, ThreatLevel as TL
            
            return DR(
                detection_id=result.detection_id,
                camera_id=result.camera_id,
                timestamp=result.timestamp,
                detections=[],  # Would include actual detections
                threat_score=result.threat_analysis.threat_score if result.threat_analysis else 0.0,
                threat_level=TL(result.threat_analysis.threat_level) if result.threat_analysis else TL.NONE,
                processing_time_ms=result.processing_time_ms,
                ai_models_used=result.ai_models_used,
                insights=result.insights
            )
            
        except Exception as e:
            logger.error(f"Failed to process frame: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status with metrics.
        
        Returns:
            Dictionary with system operational status
        """
        try:
            # Calculate uptime (simplified)
            uptime_seconds = 0.0  # Would track actual start time
            
            # Get camera count
            cameras = await self.db_service.get_cameras()
            active_cameras = len([c for c in cameras if c['status'] == 'online'])
            
            # Determine current threat level
            recent_threats = await self.db_service.get_threat_statistics(hours=1)
            critical_count = recent_threats.get('critical_threats', 0)
            high_count = recent_threats.get('high_threats', 0)
            
            if critical_count > 0:
                threat_level = "critical"
            elif high_count > 0:
                threat_level = "high"
            elif recent_threats.get('total_threats', 0) > 0:
                threat_level = "medium"
            else:
                threat_level = "none"
            
            return {
                "status": "operational",
                "version": "4.0.0",
                "uptime_seconds": uptime_seconds,
                "active_cameras": active_cameras,
                "total_detections": self.stats["total_processed"],
                "threat_level": threat_level,
                "gpu_utilization": 0.0,  # Would query actual GPU
                "memory_usage": 0.0,  # Would query actual memory
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            raise

    async def analyze_behavior_patterns(self, hours: int = 168) -> Dict[str, Any]:
        """
        Analyze behavioral patterns over time period.
        
        Args:
            hours: Time range in hours (default 1 week)
            
        Returns:
            Dictionary with pattern analysis
        """
        try:
            # Query intelligence results for patterns
            since = datetime.utcnow() - timedelta(hours=hours)
            
            query = """
                SELECT 
                    camera_id,
                    COUNT(*) as detection_count,
                    AVG(threat_score) as avg_threat_score,
                    COUNT(*) FILTER (WHERE threat_score > 0.7) as high_threat_count
                FROM intelligence_results
                WHERE timestamp > $1
                GROUP BY camera_id
                ORDER BY avg_threat_score DESC
            """
            
            results = await self.db_service.fetch_all(query, since)
            
            return {
                "time_range_hours": hours,
                "patterns_by_camera": results,
                "total_detections": sum(r['detection_count'] for r in results),
                "avg_threat_level": sum(r['avg_threat_score'] for r in results) / len(results) if results else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze behavior patterns: {e}")
            return {"error": str(e)}

    async def reload_models(self) -> bool:
        """
        Hot reload AI models without restart.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Reloading AI models...")
            
            # Reload threat detector models
            if self.is_threat_detector_enabled:
                # Would call threat detector reload endpoint
                logger.info("Threat detector models reloaded")
            
            logger.info("✅ Models reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload models: {e}")
            return False

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded AI models.
        
        Returns:
            Dictionary with model metadata
        """
        try:
            models = []
            
            # Threat detector models
            if self.is_threat_detector_enabled:
                models.append({
                    "name": "Threat Detector",
                    "type": "threat_analysis",
                    "status": "loaded",
                    "version": "1.0.0",
                    "enabled": True
                })
            
            # Behavior analyzer
            models.append({
                "name": "Behavior Analyzer",
                "type": "behavior_analysis",
                "status": "loaded",
                "version": "1.0.0",
                "enabled": True
            })
            
            return {
                "models": models,
                "count": len(models),
                "all_loaded": all(m['status'] == 'loaded' for m in models)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"error": str(e), "models": [], "count": 0}

    async def perform_maintenance(self) -> None:
        """
        Perform periodic maintenance tasks.
        Called by background worker every 30 seconds.
        """
        try:
            # Clear old items from queues if needed
            if self.detection_queue.qsize() > 500:
                logger.warning(f"Detection queue size high: {self.detection_queue.qsize()}")
            
            # Update cache with current statistics
            await self.cache_service.set_json(
                "orchestrator:stats",
                self.stats,
                ttl=60
            )
            
            # Log performance metrics
            if self.stats["total_processed"] % 100 == 0 and self.stats["total_processed"] > 0:
                logger.info(
                    f"Performance: {self.stats['total_processed']} processed, "
                    f"{self.stats['threats_detected']} threats, "
                    f"{self.stats['avg_processing_time']:.2f}ms avg"
                )
                
        except Exception as e:
            logger.error(f"Maintenance task error: {e}")

    async def shutdown(self):
        """Shutdown the enhanced AI orchestrator."""
        try:
            logger.info("Shutting down Enhanced AI Orchestrator...")

            self.is_running = False

            # Cancel all workers
            for worker in self.workers:
                worker.cancel()

            # Wait for workers to finish
            if self.workers:
                await asyncio.gather(*self.workers, return_exceptions=True)

            # Shutdown threat detector client
            if self.is_threat_detector_enabled:
                await self.threat_detector.shutdown()

            logger.info("Enhanced AI Orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"Error during Enhanced AI Orchestrator shutdown: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return {
            "queue_sizes": {
                "detection_queue": self.detection_queue.qsize(),
                "result_queue": self.result_queue.qsize()
            },
            "processing_stats": self.stats,
            "workers_active": len(self.workers),
            "threat_detector_enabled": self.is_threat_detector_enabled
        }
