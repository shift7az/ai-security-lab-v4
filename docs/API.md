# AI Security Lab v4.0 - API Documentation

## Overview

The AI Security Lab v4.0 provides comprehensive REST APIs for all core services. This documentation covers the available endpoints, request/response formats, authentication, and usage examples.

## Base URLs

- **Threat Detector Service**: `http://localhost:8001`
- **AI Orchestrator Service**: `http://localhost:8000`
- **Dashboard API**: `http://localhost:3000/api`
- **Frigate API**: `http://localhost:5000/api`

## Authentication

### API Key Authentication
```bash
# Include API key in headers
curl -H "X-API-Key: your-api-key" http://localhost:8001/analyze
```

### JWT Token Authentication (Dashboard)
```bash
# Include JWT token in Authorization header
curl -H "Authorization: Bearer your-jwt-token" http://localhost:3000/api/user/profile
```

---

## Threat Detector Service API

### Base URL: `http://localhost:8001`

### 1. Analyze Detection

Analyze a detection event for potential threats using multi-factor analysis.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "camera_id": "entrance_01",
  "detection_type": "person",
  "confidence": 0.85,
  "bbox": [100, 100, 200, 300],
  "frame_data": "base64_encoded_image_data",
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "zone": "restricted_area",
    "additional_context": {}
  }
}
```

**Response:**
```json
{
  "detection_id": "threat_1704110400_entrance_01",
  "camera_id": "entrance_01",
  "timestamp": "2024-01-01T12:00:00Z",
  "threat_score": 0.75,
  "threat_level": "HIGH",
  "factors": [
    {
      "name": "weapon_detection",
      "score": 0.9,
      "description": "Potential weapon detected in frame",
      "confidence": 0.85
    },
    {
      "name": "behavior_analysis",
      "score": 0.6,
      "description": "Suspicious movement patterns detected",
      "confidence": 0.7
    }
  ],
  "primary_threat": "weapon_detected",
  "confidence": 0.85,
  "requires_response": true,
  "response_priority": "HIGH",
  "metadata": {
    "processing_time_ms": 150,
    "models_used": ["weapon_detector", "behavior_analyzer"],
    "alert_generated": true
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "camera_id": "entrance_01",
    "detection_type": "person",
    "confidence": 0.85,
    "bbox": [100, 100, 200, 300],
    "metadata": {
      "zone": "restricted_area"
    }
  }'
```

### 2. Get Threat Statistics

Retrieve threat detection statistics for a specified time period.

**Endpoint:** `GET /stats`

**Query Parameters:**
- `hours` (optional): Time period in hours (default: 24)
- `camera_id` (optional): Filter by specific camera
- `threat_level` (optional): Filter by threat level (LOW, MEDIUM, HIGH, CRITICAL)

**Response:**
```json
{
  "time_range_hours": 24,
  "total_detections": 150,
  "threat_breakdown": {
    "CRITICAL": 2,
    "HIGH": 8,
    "MEDIUM": 25,
    "LOW": 115
  },
  "camera_breakdown": {
    "entrance_01": 45,
    "parking_lot": 30,
    "lobby": 75
  },
  "threat_types": {
    "weapon_detected": 5,
    "suspicious_behavior": 15,
    "unauthorized_access": 8,
    "crowd_anomaly": 2
  },
  "average_threat_score": 0.35,
  "alerts_generated": 35,
  "response_time_avg_ms": 125
}
```

**cURL Example:**
```bash
curl "http://localhost:8001/stats?hours=24&camera_id=entrance_01"
```

### 3. Get Threat History

Retrieve historical threat detection data.

**Endpoint:** `GET /history`

**Query Parameters:**
- `hours` (optional): Time period in hours (default: 24)
- `camera_id` (optional): Filter by specific camera
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "total_count": 250,
  "returned_count": 50,
  "threats": [
    {
      "detection_id": "threat_1704110400_entrance_01",
      "camera_id": "entrance_01",
      "timestamp": "2024-01-01T12:00:00Z",
      "threat_score": 0.85,
      "threat_level": "HIGH",
      "primary_threat": "weapon_detected",
      "requires_response": true,
      "acknowledged": false,
      "resolved": false
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### 4. Acknowledge Alert

Acknowledge a threat alert.

**Endpoint:** `POST /alerts/{alert_id}/acknowledge`

**Request Body:**
```json
{
  "user_id": "security_officer_01",
  "notes": "Alert acknowledged, investigating"
}
```

**Response:**
```json
{
  "alert_id": "alert_1704110400_001",
  "acknowledged": true,
  "acknowledged_by": "security_officer_01",
  "acknowledged_at": "2024-01-01T12:05:00Z",
  "notes": "Alert acknowledged, investigating"
}
```

### 5. Detect Faces (NEW)

Detect and analyze faces in an image using MediaPipe or InsightFace.

**Endpoint:** `POST /detect/faces`

**Request Body:**
```json
{
  "frame_data": "base64_encoded_image_data",
  "bbox": [100, 100, 200, 300],
  "use_insightface": false
}
```

**Response:**
```json
{
  "status": "success",
  "faces": [
    {
      "bbox": [120, 140, 180, 220],
      "confidence": 0.95,
      "landmarks": [
        {"x": 135, "y": 165},
        {"x": 165, "y": 165},
        {"x": 150, "y": 185}
      ],
      "embedding": [0.123, -0.456, ...],
      "age": 35,
      "gender": "male"
    }
  ],
  "count": 1,
  "model": "MediaPipe",
  "processing_time_ms": 45
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8001/detect/faces \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "frame_data": "base64_image_data",
    "use_insightface": false
  }'
```

**Features:**
- **MediaPipe**: Fast face detection with landmarks (default)
- **InsightFace**: Advanced face recognition with embeddings, age, and gender estimation
- Returns face count, bounding boxes, confidence scores
- Optional region-of-interest (bbox) for focused detection

### 6. Recognize License Plates (NEW)

Recognize license plates in an image using EasyOCR.

**Endpoint:** `POST /detect/plates`

**Request Body:**
```json
{
  "frame_data": "base64_encoded_image_data",
  "bbox": [100, 100, 400, 200]
}
```

**Response:**
```json
{
  "status": "success",
  "plates": [
    {
      "text": "ABC1234",
      "raw_text": "ABC-1234",
      "confidence": 0.92,
      "bbox": [[120, 130], [380, 130], [380, 180], [120, 180]],
      "pattern_match": "US"
    }
  ],
  "count": 1,
  "model": "EasyOCR",
  "languages": ["en"],
  "processing_time_ms": 320
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8001/detect/plates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "frame_data": "base64_image_data"
  }'
```

**Features:**
- Multi-language OCR support (default: English)
- Pattern matching for US, international plates
- Preprocessing for improved accuracy (denoising, thresholding)
- Confidence scores and bounding boxes
- Common OCR corrections (O→0, I→1)

### 7. Comprehensive Detection (NEW)

Run all AI models (weapon, face, plate) on a single image.

**Endpoint:** `POST /detect/comprehensive`

**Request Body:**
```json
{
  "frame_data": "base64_encoded_image_data",
  "camera_id": "entrance_01",
  "detection_type": "person",
  "use_insightface": false
}
```

**Response:**
```json
{
  "status": "success",
  "weapon_detection": {
    "detected": true,
    "confidence": 0.85,
    "weapon_type": "gun",
    "model": "YOLOv8"
  },
  "face_detection": {
    "faces": [
      {
        "bbox": [120, 140, 180, 220],
        "confidence": 0.95,
        "landmarks": [...]
      }
    ],
    "count": 1,
    "model": "MediaPipe"
  },
  "plate_recognition": {
    "plates": [
      {
        "text": "ABC1234",
        "confidence": 0.92,
        "pattern_match": "US"
      }
    ],
    "count": 1,
    "model": "EasyOCR"
  },
  "processing_time_ms": 425
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8001/detect/comprehensive \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "frame_data": "base64_image_data",
    "camera_id": "entrance_01",
    "detection_type": "person"
  }'
```

**Use Cases:**
- Complete situational awareness with single API call
- Batch processing for forensic analysis
- Testing and debugging all models simultaneously
- Performance benchmarking

### 8. Get Models Information (NEW)

Get detailed information about all loaded AI models.

**Endpoint:** `GET /models/info`

**Response:**
```json
{
  "weapon_detector": {
    "model_type": "YOLOv8",
    "model_path": "yolov8n.pt",
    "yolo_available": true,
    "using_ml_model": true,
    "weapon_classes": ["gun", "rifle", "pistol", "knife", "sword", ...],
    "threat_objects": ["knife", "baseball bat", "bottle", "scissors"],
    "confidence_threshold": 0.5,
    "device": "cuda",
    "cuda_available": true,
    "is_initialized": true
  },
  "face_detector": {
    "model_type": "MediaPipe",
    "insightface_available": true,
    "mediapipe_available": true,
    "using_ml_model": true,
    "min_detection_confidence": 0.5,
    "is_initialized": true,
    "capabilities": {
      "detection": true,
      "recognition": false,
      "age_gender": false,
      "embeddings": false
    }
  },
  "plate_recognizer": {
    "model_type": "EasyOCR",
    "easyocr_available": true,
    "using_ml_model": true,
    "languages": ["en"],
    "using_gpu": true,
    "supported_patterns": ["US", "US_FULL", "GENERIC"],
    "is_initialized": true
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8001/models/info \
  -H "X-API-Key: your-api-key"
```

**Features:**
- Check which models are loaded and initialized
- Verify GPU/CUDA availability
- See supported detection classes and patterns
- Useful for debugging and monitoring

---

## 7-Factor Threat Analysis System

The `/analyze` endpoint uses a comprehensive 7-factor threat scoring system:

| Factor | Weight | Description | AI Model |
|--------|--------|-------------|----------|
| **1. Object Type Analysis** | 15% | Base threat level by object class | Rule-based |
| **2. Weapon Detection** | 30% | ML-based weapon and firearm detection | **YOLOv8** |
| **3. Behavior Analysis** | 20% | Movement patterns, dwell time, suspicious activity | Rule-based |
| **4. Context Analysis** | 10% | Time of day, location, crowd density | Rule-based |
| **5. Historical Analysis** | 5% | Recent threats in area | Database |
| **6. Face Recognition** | 10% | Watchlist matching, unknown persons | **MediaPipe/InsightFace** |
| **7. Vehicle/Plate Analysis** | 10% | License plate recognition, stolen vehicles | **EasyOCR** |

**Total ML Contribution**: 50% (Factors 2, 6, 7 use machine learning models)

**Threat Level Thresholds:**
- **CRITICAL**: threat_score ≥ 0.80
- **HIGH**: 0.60 ≤ threat_score < 0.80
- **MEDIUM**: 0.40 ≤ threat_score < 0.60
- **LOW**: threat_score < 0.40

**Example Updated Response with All Factors:**
```json
{
  "detection_id": "threat_1704110400_entrance_01",
  "threat_score": 0.78,
  "threat_level": "HIGH",
  "factors": [
    {
      "name": "object_type",
      "score": 0.5,
      "weight": 0.15,
      "description": "Person detected in monitored area"
    },
    {
      "name": "weapon_detection",
      "score": 0.9,
      "weight": 0.30,
      "description": "YOLOv8 detected potential firearm",
      "model": "YOLOv8",
      "confidence": 0.87
    },
    {
      "name": "behavior_analysis",
      "score": 0.7,
      "weight": 0.20,
      "description": "Erratic movement patterns detected"
    },
    {
      "name": "context_analysis",
      "score": 0.6,
      "weight": 0.10,
      "description": "Restricted area during off-hours"
    },
    {
      "name": "historical_analysis",
      "score": 0.4,
      "weight": 0.05,
      "description": "No recent threats in area"
    },
    {
      "name": "face_recognition",
      "score": 0.8,
      "weight": 0.10,
      "description": "Unknown person with obscured face",
      "model": "MediaPipe",
      "faces_detected": 1
    },
    {
      "name": "vehicle_analysis",
      "score": 0.3,
      "weight": 0.10,
      "description": "No vehicles detected",
      "model": "EasyOCR"
    }
  ],
  "models_used": ["YOLOv8", "MediaPipe", "EasyOCR"],
  "ml_confidence": 0.85
}
```

---

## AI Orchestrator Service API

### Base URL: `http://localhost:8000`

### Authentication Endpoints

#### 1. Login

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_123",
    "username": "admin",
    "role": "admin",
    "email": "admin@example.com"
  }
}
```

#### 2. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Dashboard Endpoints

#### 1. Get Camera List

**Endpoint:** `GET /api/dashboard/cameras`

**Response:**
```json
{
  "cameras": [
    {
      "id": "entrance_01",
      "name": "Main Entrance",
      "location": "Building A - Entrance",
      "status": "online",
      "stream_url": "rtsp://...",
      "detections_today": 145,
      "threats_today": 8,
      "last_detection": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 12,
  "online": 11,
  "offline": 1
}
```

#### 2. Get Alerts

**Endpoint:** `GET /api/dashboard/alerts`

**Query Parameters:**
- `status` (optional): Filter by status (open, acknowledged, resolved)
- `severity` (optional): Filter by severity (critical, high, medium, low)
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_1704110400_001",
      "camera_id": "entrance_01",
      "timestamp": "2024-01-01T12:00:00Z",
      "severity": "high",
      "title": "Weapon Detected",
      "description": "Potential firearm detected in main entrance",
      "threat_score": 0.85,
      "status": "open",
      "acknowledged": false,
      "resolved": false,
      "thumbnail_url": "/api/media/thumbnails/alert_1704110400_001.jpg"
    }
  ],
  "total": 35,
  "unacknowledged": 12
}
```

#### 3. Get Timeline Events

**Endpoint:** `GET /api/dashboard/timeline`

**Query Parameters:**
- `hours` (optional): Time period (default: 24)
- `camera_id` (optional): Filter by camera
- `limit` (optional): Maximum results (default: 100)

**Response:**
```json
{
  "events": [
    {
      "id": "event_1704110400_001",
      "timestamp": "2024-01-01T12:00:00Z",
      "type": "threat_detected",
      "camera_id": "entrance_01",
      "severity": "high",
      "description": "Weapon detected at main entrance",
      "metadata": {
        "threat_score": 0.85,
        "detection_type": "person",
        "models_used": ["YOLOv8", "MediaPipe"]
      }
    }
  ],
  "total": 487,
  "time_range_hours": 24
}
```

#### 4. Get System Statistics

**Endpoint:** `GET /api/dashboard/stats`

**Query Parameters:**
- `period` (optional): Time period (hour, day, week, month)

**Response:**
```json
{
  "period": "day",
  "timestamp": "2024-01-01T12:00:00Z",
  "detections": {
    "total": 1547,
    "by_type": {
      "person": 1123,
      "vehicle": 398,
      "animal": 26
    }
  },
  "threats": {
    "total": 47,
    "by_level": {
      "critical": 2,
      "high": 12,
      "medium": 18,
      "low": 15
    }
  },
  "alerts": {
    "generated": 47,
    "acknowledged": 35,
    "resolved": 28,
    "open": 12
  },
  "system_health": {
    "cameras_online": 11,
    "cameras_total": 12,
    "ai_models_active": 3,
    "avg_processing_time_ms": 145,
    "api_uptime_pct": 99.8
  }
}
```

---

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: camera_id",
    "details": {
      "field": "camera_id",
      "requirement": "required"
    }
  },
  "request_id": "req_1704110400_abc123"
}
```

**Common Error Codes:**
- `INVALID_REQUEST`: Malformed request or missing required fields
- `AUTHENTICATION_FAILED`: Invalid API key or JWT token
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

**HTTP Status Codes:**
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service down

---

## Rate Limiting

API endpoints are rate-limited to ensure fair usage:

- **Threat Detector**: 100 requests/minute per API key
- **Dashboard API**: 1000 requests/minute per user
- **Authentication**: 10 requests/minute per IP

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704110460
```

---

## Webhooks (Future)

Webhook support for real-time notifications is planned for v5.0:

- `threat.detected`: New threat detected
- `alert.created`: Alert generated
- `alert.acknowledged`: Alert acknowledged
- `camera.offline`: Camera went offline
- `system.health`: System health change

---

## SDK Support (Future)

Official SDKs are planned:
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

---

## Additional Resources

- **OpenAPI Spec**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc` (Alternative API docs)
- **Postman Collection**: Available in `/docs/postman/`
- **Example Code**: Available in `/examples/`

---

## Support

For API support:
- GitHub Issues: https://github.com/shift7az/ai-security-lab-v4/issues
- Documentation: https://github.com/shift7az/ai-security-lab-v4/docs
- Email: support@example.com
