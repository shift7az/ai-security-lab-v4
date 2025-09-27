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
  "acknowledge
