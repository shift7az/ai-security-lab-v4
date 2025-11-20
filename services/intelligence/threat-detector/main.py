"""
AI Security Lab v4.0 - Threat Detector Service

Advanced threat detection service that analyzes multiple factors to provide
real-time threat scoring and automated security responses.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import redis.asyncio as redis
from opentelemetry import trace
import torch
import cv2

from src.models.threat_model import ThreatModel, ThreatFactor
from src.detectors.weapon_detector import WeaponDetector
from src.detectors.behavior_analyzer import BehaviorAnalyzer
from src.detectors.face_detector import FaceDetector
from src.detectors.plate_recognizer import PlateRecognizer
from src.utils.alert_manager import AlertManager
from src.config.settings import Settings


# ============================================================================
# CONFIGURATION AND LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

settings = Settings()


# ============================================================================
# DATA MODELS
# ============================================================================

class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatFactor(BaseModel):
    """Individual threat factor."""
    name: str
    score: float
    weight: float
    description: str
    confidence: float


class ThreatAnalysis(BaseModel):
    """Complete threat analysis result."""
    detection_id: str
    camera_id: str
    timestamp: datetime
    threat_score: float
    threat_level: ThreatLevel
    factors: List[ThreatFactor]
    primary_threat: str
    confidence: float
    requires_response: bool
    response_priority: int
    metadata: Dict[str, Any]


class DetectionInput(BaseModel):
    """Input for threat analysis."""
    camera_id: str
    detection_type: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    frame_data: Optional[str] = None  # base64 encoded image
    metadata: Dict[str, Any] = {}


# ============================================================================
# THREAT DETECTOR SERVICE
# ============================================================================

class ThreatDetectorService:
    """
    Advanced threat detection service with multi-factor analysis.
    """

    def __init__(self):
        self.threat_model = ThreatModel()
        self.weapon_detector = WeaponDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.face_detector = FaceDetector()
        self.plate_recognizer = PlateRecognizer()
        self.alert_manager = AlertManager()
        self.db_pool = None
        self.redis_client = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    async def initialize(self):
        """Initialize the threat detector service."""
        try:
            # Database connection
            self.db_pool = await asyncpg.create_pool(
                host="timescaledb",
                port=5432,
                database="security_events",
                user="security",
                password=settings.database_password,
                min_size=5,
                max_size=20
            )

            # Redis connection
            self.redis_client = redis.Redis(
                host="redis-stack",
                port=6379,
                password=settings.redis_password,
                decode_responses=True
            )

            # Initialize ML models
            await self.threat_model.load_models()
            await self.weapon_detector.initialize()
            await self.behavior_analyzer.initialize()
            await self.face_detector.initialize()
            await self.plate_recognizer.initialize()

            logger.info("✅ Threat detector service initialized successfully")
            logger.info(f"  - Weapon detection: {self.weapon_detector.get_model_info()['model_type']}")
            logger.info(f"  - Face detection: {self.face_detector.get_model_info()['model_type']}")
            logger.info(f"  - Plate recognition: {self.plate_recognizer.get_model_info()['model_type']}")

        except Exception as e:
            logger.error(f"Failed to initialize threat detector: {e}")
            raise

    async def analyze_threat(self, detection: DetectionInput) -> ThreatAnalysis:
        """
        Analyze a detection for threat potential.

        Args:
            detection: Input detection data

        Returns:
            Complete threat analysis
        """
        with trace.get_tracer(__name__).start_as_current_span("analyze_threat") as span:
            span.set_attribute("detection.type", detection.detection_type)
            span.set_attribute("camera.id", detection.camera_id)

            try:
                factors = []
                detection_id = f"threat_{datetime.utcnow().timestamp()}_{detection.camera_id}"

                # Factor 1: Object Type Analysis
                object_factor = await self._analyze_object_type(detection)
                factors.append(object_factor)

                # Factor 2: Weapon Detection
                weapon_factor = await self._analyze_weapon_threat(detection)
                factors.append(weapon_factor)

                # Factor 3: Behavior Analysis
                behavior_factor = await self._analyze_behavior_threat(detection)
                factors.append(behavior_factor)

                # Factor 4: Context Analysis
                context_factor = await self._analyze_context_threat(detection)
                factors.append(context_factor)

                # Factor 5: Historical Analysis
                historical_factor = await self._analyze_historical_threat(detection)
                factors.append(historical_factor)

                # Factor 6: Face Recognition (for person detections)
                face_factor = await self._analyze_face_threat(detection)
                factors.append(face_factor)

                # Factor 7: Vehicle/Plate Analysis (for vehicle detections)
                vehicle_factor = await self._analyze_vehicle_threat(detection)
                factors.append(vehicle_factor)

                # Calculate overall threat score
                threat_score = self._calculate_threat_score(factors)
                threat_level = self._determine_threat_level(threat_score)
                primary_threat = self._identify_primary_threat(factors)

                # Determine if response is required
                requires_response = threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
                response_priority = self._calculate_response_priority(threat_score, factors)

                analysis = ThreatAnalysis(
                    detection_id=detection_id,
                    camera_id=detection.camera_id,
                    timestamp=datetime.utcnow(),
                    threat_score=threat_score,
                    threat_level=threat_level,
                    factors=factors,
                    primary_threat=primary_threat,
                    confidence=self._calculate_overall_confidence(factors),
                    requires_response=requires_response,
                    response_priority=response_priority,
                    metadata={
                        "detection_type": detection.detection_type,
                        "bbox": detection.bbox,
                        "processing_time_ms": 0  # Will be set by caller
                    }
                )

                # Store analysis in database
                await self._store_threat_analysis(analysis)

                # Cache for real-time access
                await self._cache_threat_analysis(analysis)

                # Trigger alerts if needed
                if requires_response:
                    await self._trigger_threat_alert(analysis)

                logger.info(f"Threat analysis completed: {threat_level.value} (score: {threat_score:.3f})")
                return analysis

            except Exception as e:
                logger.error(f"Error in threat analysis: {e}")
                raise

    async def _analyze_object_type(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze threat based on object type."""
        object_threat_scores = {
            "weapon": 0.9,
            "person": 0.3,
            "vehicle": 0.2,
            "package": 0.6,
            "animal": 0.1
        }

        base_score = object_threat_scores.get(detection.detection_type, 0.3)
        confidence = detection.confidence

        # Adjust based on context
        if detection.detection_type == "person":
            # Higher threat if person is in restricted area
            if detection.metadata.get("in_restricted_area"):
                base_score += 0.3
            # Lower threat if person is known/authorized
            if detection.metadata.get("person_recognized"):
                base_score -= 0.2

        return ThreatFactor(
            name="object_type",
            score=min(base_score * confidence, 1.0),
            weight=0.15,  # Reduced from 0.25 to accommodate new factors
            description=f"Object type: {detection.detection_type}",
            confidence=confidence
        )

    async def _analyze_weapon_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze weapon threat using computer vision."""
        try:
            if detection.frame_data and detection.detection_type in ["person", "weapon"]:
                # Use weapon detection model
                weapon_score = await self.weapon_detector.detect_weapon(
                    detection.frame_data,
                    detection.bbox
                )
            else:
                weapon_score = 0.0

            return ThreatFactor(
                name="weapon_detection",
                score=weapon_score,
                weight=0.30,  # Reduced from 0.35 to accommodate new factors
                description="Weapon detection analysis",
                confidence=0.85 if weapon_score > 0.5 else 0.95
            )

        except Exception as e:
            logger.warning(f"Weapon detection failed: {e}")
            return ThreatFactor(
                name="weapon_detection",
                score=0.0,
                weight=0.30,  # Reduced from 0.35 to accommodate new factors
                description="Weapon detection unavailable",
                confidence=0.0
            )

    async def _analyze_behavior_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze behavioral threat patterns."""
        try:
            behavior_score = await self.behavior_analyzer.analyze_behavior(
                detection.camera_id,
                detection.detection_type,
                detection.metadata
            )

            return ThreatFactor(
                name="behavior_analysis",
                score=behavior_score,
                weight=0.20,  # Reduced from 0.25 to accommodate new factors
                description="Behavioral pattern analysis",
                confidence=0.75
            )

        except Exception as e:
            logger.warning(f"Behavior analysis failed: {e}")
            return ThreatFactor(
                name="behavior_analysis",
                score=0.3,
                weight=0.20,  # Reduced from 0.25 to accommodate new factors
                description="Behavior analysis unavailable",
                confidence=0.0
            )

    async def _analyze_context_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze contextual threat factors."""
        context_score = 0.0
        reasons = []

        # Time-based analysis
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Night time
            context_score += 0.2
            reasons.append("night_time")

        # Location-based analysis
        if detection.metadata.get("in_restricted_area"):
            context_score += 0.3
            reasons.append("restricted_area")

        # Crowd analysis
        crowd_density = detection.metadata.get("crowd_density", 0)
        if crowd_density > 0.8:  # High crowd density
            context_score += 0.2
            reasons.append("high_crowd_density")

        return ThreatFactor(
            name="context_analysis",
            score=min(context_score, 1.0),
            weight=0.10,
            description=f"Context factors: {', '.join(reasons)}",
            confidence=0.80
        )

    async def _analyze_historical_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze historical threat patterns."""
        try:
            # Check recent threats in same area
            recent_threats = await self._get_recent_threats(
                detection.camera_id,
                hours=24
            )

            historical_score = 0.0
            if recent_threats:
                # Higher score if recent threats in same area
                historical_score = min(len(recent_threats) * 0.1, 0.5)

            return ThreatFactor(
                name="historical_analysis",
                score=historical_score,
                weight=0.05,
                description=f"Recent threats in area: {len(recent_threats)}",
                confidence=0.90
            )

        except Exception as e:
            logger.warning(f"Historical analysis failed: {e}")
            return ThreatFactor(
                name="historical_analysis",
                score=0.0,
                weight=0.05,
                description="Historical analysis unavailable",
                confidence=0.0
            )

    async def _analyze_face_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze face-based threats (watchlist, unknown persons, etc.)."""
        try:
            if detection.frame_data and detection.detection_type == "person":
                # Run face detection
                face_results = await self.face_detector.detect_faces(
                    detection.frame_data,
                    detection.bbox
                )

                face_count = face_results.get("count", 0)
                faces = face_results.get("faces", [])

                face_score = 0.0
                description_parts = []

                if face_count == 0:
                    # No face detected on person - suspicious (mask, hidden face)
                    face_score = 0.4
                    description_parts.append("no_face_detected")
                elif face_count > 0:
                    # Face detected - check against watchlist
                    # TODO: Implement watchlist matching with face embeddings
                    is_on_watchlist = detection.metadata.get("on_watchlist", False)
                    is_unknown = detection.metadata.get("unknown_person", False)

                    if is_on_watchlist:
                        face_score = 0.9
                        description_parts.append("watchlist_match")
                    elif is_unknown and detection.metadata.get("in_restricted_area"):
                        face_score = 0.6
                        description_parts.append("unknown_in_restricted")
                    else:
                        face_score = 0.1
                        description_parts.append("face_detected")

                    description_parts.append(f"{face_count}_faces")

                return ThreatFactor(
                    name="face_recognition",
                    score=face_score,
                    weight=0.10,
                    description=f"Face analysis: {', '.join(description_parts)}",
                    confidence=0.80 if face_count > 0 else 0.60
                )
            else:
                # Not a person detection, face analysis not applicable
                return ThreatFactor(
                    name="face_recognition",
                    score=0.0,
                    weight=0.10,
                    description="Face analysis not applicable",
                    confidence=1.0
                )

        except Exception as e:
            logger.warning(f"Face analysis failed: {e}")
            return ThreatFactor(
                name="face_recognition",
                score=0.0,
                weight=0.10,
                description="Face analysis unavailable",
                confidence=0.0
            )

    async def _analyze_vehicle_threat(self, detection: DetectionInput) -> ThreatFactor:
        """Analyze vehicle-based threats (watchlist plates, stolen vehicles, etc.)."""
        try:
            if detection.frame_data and detection.detection_type == "vehicle":
                # Run license plate recognition
                plate_results = await self.plate_recognizer.recognize_plate(
                    detection.frame_data,
                    detection.bbox
                )

                plate_count = plate_results.get("count", 0)
                plates = plate_results.get("plates", [])

                vehicle_score = 0.0
                description_parts = []

                if plate_count == 0:
                    # No plate detected - suspicious
                    vehicle_score = 0.3
                    description_parts.append("no_plate_detected")
                elif plate_count > 0:
                    # Plate detected - check against watchlist
                    best_plate = plates[0]  # Highest confidence
                    plate_text = best_plate.get("text", "")
                    plate_conf = best_plate.get("confidence", 0.0)

                    # TODO: Implement watchlist matching
                    is_stolen = detection.metadata.get("stolen_vehicle", False)
                    is_on_watchlist = detection.metadata.get("on_watchlist", False)
                    parking_violation = detection.metadata.get("parking_violation", False)

                    if is_stolen or is_on_watchlist:
                        vehicle_score = 0.9
                        description_parts.append("watchlist_match")
                    elif parking_violation:
                        vehicle_score = 0.4
                        description_parts.append("parking_violation")
                    else:
                        vehicle_score = 0.1
                        description_parts.append("vehicle_identified")

                    description_parts.append(f"plate:{plate_text}")

                return ThreatFactor(
                    name="vehicle_analysis",
                    score=vehicle_score,
                    weight=0.10,
                    description=f"Vehicle analysis: {', '.join(description_parts)}",
                    confidence=0.85 if plate_count > 0 else 0.50
                )
            else:
                # Not a vehicle detection, vehicle analysis not applicable
                return ThreatFactor(
                    name="vehicle_analysis",
                    score=0.0,
                    weight=0.10,
                    description="Vehicle analysis not applicable",
                    confidence=1.0
                )

        except Exception as e:
            logger.warning(f"Vehicle analysis failed: {e}")
            return ThreatFactor(
                name="vehicle_analysis",
                score=0.0,
                weight=0.10,
                description="Vehicle analysis unavailable",
                confidence=0.0
            )

    def _calculate_threat_score(self, factors: List[ThreatFactor]) -> float:
        """Calculate weighted threat score from all factors."""
        total_weight = sum(factor.weight for factor in factors)
        weighted_score = sum(
            factor.score * factor.weight
            for factor in factors
        )

        return min(weighted_score / total_weight if total_weight > 0 else 0.0, 1.0)

    def _determine_threat_level(self, threat_score: float) -> ThreatLevel:
        """Determine threat level from score."""
        if threat_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            return ThreatLevel.HIGH
        elif threat_score >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _identify_primary_threat(self, factors: List[ThreatFactor]) -> str:
        """Identify the primary threat factor."""
        primary = max(factors, key=lambda f: f.score * f.weight)
        return primary.name

    def _calculate_overall_confidence(self, factors: List[ThreatFactor]) -> float:
        """Calculate overall confidence in the analysis."""
        if not factors:
            return 0.0

        # Weight confidence by factor importance
        weighted_confidence = sum(
            factor.confidence * factor.weight
            for factor in factors
        )
        total_weight = sum(factor.weight for factor in factors)

        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _calculate_response_priority(self, threat_score: float, factors: List[ThreatFactor]) -> int:
        """Calculate response priority (1-10, 10 being highest)."""
        priority = int(threat_score * 10)

        # Increase priority for weapon detection
        if any(f.name == "weapon_detection" and f.score > 0.5 for f in factors):
            priority += 2

        return min(priority, 10)

    async def _get_recent_threats(self, camera_id: str, hours: int) -> List[Dict]:
        """Get recent threats for a camera."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            query = """
                SELECT threat_score, threat_level, timestamp
                FROM threat_analyses
                WHERE camera_id = $1 AND timestamp > $2 AND threat_score > 0.5
                ORDER BY timestamp DESC
            """

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, camera_id, since)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent threats: {e}")
            return []

    async def _store_threat_analysis(self, analysis: ThreatAnalysis):
        """Store threat analysis in database."""
        try:
            query = """
                INSERT INTO threat_analyses (
                    detection_id, camera_id, timestamp, threat_score,
                    threat_level, factors, primary_threat, confidence,
                    requires_response, response_priority, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """

            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    analysis.detection_id,
                    analysis.camera_id,
                    analysis.timestamp,
                    analysis.threat_score,
                    analysis.threat_level.value,
                    json.dumps([f.dict() for f in analysis.factors]),
                    analysis.primary_threat,
                    analysis.confidence,
                    analysis.requires_response,
                    analysis.response_priority,
                    json.dumps(analysis.metadata)
                )

        except Exception as e:
            logger.error(f"Failed to store threat analysis: {e}")

    async def _cache_threat_analysis(self, analysis: ThreatAnalysis):
        """Cache threat analysis for real-time access."""
        try:
            cache_key = f"threat:{analysis.detection_id}"
            cache_data = analysis.dict()

            await self.redis_client.setex(
                cache_key,
                timedelta(minutes=60),  # Cache for 1 hour
                json.dumps(cache_data, default=str)
            )

            # Also cache by camera for quick lookup
            camera_key = f"threats:camera:{analysis.camera_id}"
            await self.redis_client.zadd(
                camera_key,
                {analysis.detection_id: analysis.timestamp.timestamp()}
            )

            # Set expiry for camera cache
            await self.redis_client.expire(camera_key, timedelta(hours=24))

        except Exception as e:
            logger.error(f"Failed to cache threat analysis: {e}")

    async def _trigger_threat_alert(self, analysis: ThreatAnalysis):
        """Trigger alert for high-priority threats."""
        try:
            await self.alert_manager.create_alert({
                "type": "threat_detected",
                "level": analysis.threat_level.value,
                "camera_id": analysis.camera_id,
                "detection_id": analysis.detection_id,
                "threat_score": analysis.threat_score,
                "primary_threat": analysis.primary_threat,
                "timestamp": analysis.timestamp,
                "requires_response": analysis.requires_response,
                "response_priority": analysis.response_priority
            })

        except Exception as e:
            logger.error(f"Failed to trigger threat alert: {e}")

    async def get_threat_history(
        self,
        camera_id: Optional[str] = None,
        hours: int = 24,
        min_score: float = 0.0
    ) -> List[ThreatAnalysis]:
        """Get threat history with filtering."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            query = """
                SELECT * FROM threat_analyses
                WHERE timestamp > $1 AND threat_score >= $2
            """

            params = [since, min_score]

            if camera_id:
                query += " AND camera_id = $3"
                params.append(camera_id)

            query += " ORDER BY timestamp DESC"

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)

            return [
                ThreatAnalysis(
                    detection_id=row['detection_id'],
                    camera_id=row['camera_id'],
                    timestamp=row['timestamp'],
                    threat_score=row['threat_score'],
                    threat_level=ThreatLevel(row['threat_level']),
                    factors=[ThreatFactor(**f) for f in row['factors']],
                    primary_threat=row['primary_threat'],
                    confidence=row['confidence'],
                    requires_response=row['requires_response'],
                    response_priority=row['response_priority'],
                    metadata=row['metadata']
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get threat history: {e}")
            return []

    async def shutdown(self):
        """Shutdown the threat detector service."""
        try:
            if self.db_pool:
                await self.db_pool.close()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Threat detector service shutdown complete")
        except Exception as e:
            logger.error(f"Error during threat detector shutdown: {e}")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="AI Security Lab v4.0 - Threat Detector",
    description="Advanced threat detection and analysis service",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global threat detector instance
threat_detector: Optional[ThreatDetectorService] = None


@app.on_event("startup")
async def startup_event():
    """Application startup."""
    global threat_detector

    threat_detector = ThreatDetectorService()
    await threat_detector.initialize()
    logger.info("Threat detector service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    global threat_detector

    if threat_detector:
        await threat_detector.shutdown()
    logger.info("Threat detector service shutdown")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "threat-detector",
        "timestamp": datetime.utcnow()
    }


@app.post("/analyze", response_model=ThreatAnalysis)
async def analyze_threat_endpoint(detection: DetectionInput):
    """Analyze a detection for threats."""
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        analysis = await threat_detector.analyze_threat(detection)
        return analysis
    except Exception as e:
        logger.error(f"Threat analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/history", response_model=List[ThreatAnalysis])
async def get_threat_history(
    camera_id: Optional[str] = None,
    hours: int = 24,
    min_score: float = 0.0
):
    """Get threat history."""
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        history = await threat_detector.get_threat_history(
            camera_id=camera_id,
            hours=hours,
            min_score=min_score
        )
        return history
    except Exception as e:
        logger.error(f"Failed to get threat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@app.get("/stats")
async def get_threat_stats(hours: int = 24):
    """Get threat statistics."""
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        history = await threat_detector.get_threat_history(hours=hours)

        if not history:
            return {
                "total_threats": 0,
                "threat_levels": {},
                "average_score": 0.0,
                "requires_response": 0
            }

        # Calculate statistics
        threat_levels = {}
        for analysis in history:
            level = analysis.threat_level.value
            threat_levels[level] = threat_levels.get(level, 0) + 1

        requires_response = sum(1 for a in history if a.requires_response)
        average_score = sum(a.threat_score for a in history) / len(history)

        return {
            "total_threats": len(history),
            "threat_levels": threat_levels,
            "average_score": round(average_score, 3),
            "requires_response": requires_response,
            "time_range_hours": hours
        }

    except Exception as e:
        logger.error(f"Failed to get threat stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# ============================================================================
# SPECIALIZED DETECTION ENDPOINTS
# ============================================================================

class FaceDetectionInput(BaseModel):
    """Input for face detection."""
    frame_data: str  # base64 encoded image
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]


class PlateRecognitionInput(BaseModel):
    """Input for license plate recognition."""
    frame_data: str  # base64 encoded image
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]


class ComprehensiveDetectionInput(BaseModel):
    """Input for comprehensive detection."""
    frame_data: str  # base64 encoded image
    detection_type: str = "unknown"  # person, vehicle, etc.


@app.post("/detect/faces")
async def detect_faces_endpoint(input: FaceDetectionInput):
    """
    Specialized endpoint for face detection.

    Returns face detection results including bounding boxes, landmarks,
    and optional age/gender if InsightFace is enabled.
    """
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        results = await threat_detector.face_detector.detect_faces(
            input.frame_data,
            input.bbox
        )

        return {
            "status": "success",
            "model": results.get("model", "Unknown"),
            "faces": results.get("faces", []),
            "count": results.get("count", 0),
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Face detection failed: {str(e)}")


@app.post("/detect/plates")
async def detect_plates_endpoint(input: PlateRecognitionInput):
    """
    Specialized endpoint for license plate recognition.

    Returns license plate OCR results including text, confidence, and bounding boxes.
    """
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        results = await threat_detector.plate_recognizer.recognize_plate(
            input.frame_data,
            input.bbox
        )

        return {
            "status": "success",
            "model": results.get("model", "Unknown"),
            "plates": results.get("plates", []),
            "count": results.get("count", 0),
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Plate recognition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plate recognition failed: {str(e)}")


@app.post("/detect/comprehensive")
async def comprehensive_detection_endpoint(input: ComprehensiveDetectionInput):
    """
    Comprehensive detection endpoint that runs ALL AI models.

    Returns results from weapon detection, face detection, and plate recognition
    in a single response. Useful for analyzing a scene with all available models.
    """
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        results = {
            "status": "success",
            "timestamp": datetime.utcnow(),
            "detection_type": input.detection_type,
            "models_used": [],
            "weapon_detection": None,
            "face_detection": None,
            "plate_recognition": None
        }

        # Run all applicable models
        try:
            weapon_score = await threat_detector.weapon_detector.detect_weapon(
                input.frame_data
            )
            results["weapon_detection"] = {
                "score": weapon_score,
                "detected": weapon_score > threat_detector.weapon_detector.confidence_threshold,
                "model": threat_detector.weapon_detector.get_model_info()["model_type"]
            }
            results["models_used"].append("weapon_detection")
        except Exception as e:
            logger.warning(f"Weapon detection failed in comprehensive: {e}")

        # Face detection (if person or unknown)
        if input.detection_type in ["person", "unknown"]:
            try:
                face_results = await threat_detector.face_detector.detect_faces(
                    input.frame_data
                )
                results["face_detection"] = face_results
                results["models_used"].append("face_detection")
            except Exception as e:
                logger.warning(f"Face detection failed in comprehensive: {e}")

        # Plate recognition (if vehicle or unknown)
        if input.detection_type in ["vehicle", "unknown"]:
            try:
                plate_results = await threat_detector.plate_recognizer.recognize_plate(
                    input.frame_data
                )
                results["plate_recognition"] = plate_results
                results["models_used"].append("plate_recognition")
            except Exception as e:
                logger.warning(f"Plate recognition failed in comprehensive: {e}")

        return results

    except Exception as e:
        logger.error(f"Comprehensive detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive detection failed: {str(e)}")


@app.get("/models/info")
async def get_models_info():
    """
    Get information about all loaded AI models.

    Returns model types, availability, and configuration for each detector.
    """
    if not threat_detector:
        raise HTTPException(status_code=503, detail="Threat detector not initialized")

    try:
        return {
            "weapon_detector": threat_detector.weapon_detector.get_model_info(),
            "face_detector": threat_detector.face_detector.get_model_info(),
            "plate_recognizer": threat_detector.plate_recognizer.get_model_info(),
            "behavior_analyzer": threat_detector.behavior_analyzer.get_behavior_patterns()
        }

    except Exception as e:
        logger.error(f"Failed to get models info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models info")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
