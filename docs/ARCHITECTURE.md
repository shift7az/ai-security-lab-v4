# AI Security Lab v4.0 - System Architecture

## Overview

The AI Security Lab v4.0 is built on a modern microservices architecture designed for scalability, reliability, and real-time performance. The system leverages GPU acceleration, containerization, and event-driven processing to deliver enterprise-grade intelligent surveillance capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI Security Lab v4.0                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Input Layer                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │   Camera    │  │   Camera    │  │   Camera    │  │     ...     │        │
│ │   Feed 1    │  │   Feed 2    │  │   Feed N    │  │             │        │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                           Detection Layer                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │                        Frigate Plus                                     │ │
│ │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │ │
│ │  │   Object    │  │   Motion    │  │   Audio     │                     │ │
│ │  │ Detection   │  │ Detection   │  │ Detection   │                     │ │
│ │  └─────────────┘  └─────────────┘  └─────────────┘                     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Intelligence Layer                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │ Enhanced AI │  │   Threat    │  │   Object    │  │   Pattern   │        │
│ │Orchestrator │  │  Detector   │  │  Tracker    │  │  Analyzer   │        │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                           Data Layer                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │TimescaleDB  │  │    Redis    │  │   Qdrant    │  │    MinIO    │        │
│ │(Time-series)│  │  (Cache)    │  │ (Vectors)   │  │  (Objects)  │        │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                        Presentation Layer                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │  Dashboard  │  │ Mobile App  │  │    API      │  │ Automation  │        │
│ │  (Next.js)  │  │(React Nat.) │  │  Gateway    │  │   (n8n)     │        │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Detection Layer

#### Frigate Plus
- **Purpose**: Primary object detection and video processing
- **Technology**: GPU-accelerated YOLO models with TensorRT optimization
- **Capabilities**:
  - Real-time object detection (person, vehicle, animal, package)
  - Motion detection and tracking
  - Audio event detection
  - Zone-based analytics
  - License plate recognition
  - Face detection and recognition

#### Configuration
```yaml
# Frigate Plus features
plus:
  enabled: true
  api_key: ${PLUS_API_KEY}
  models:
    - face_recognition: true
    - license_plate: true
    - package_detection: true
    - animal_species: true
    - vehicle_attributes: true
    - person_attributes: true
```

### 2. Intelligence Layer

#### Enhanced AI Orchestrator
- **Purpose**: Coordinates multiple AI services and manages intelligence pipeline
- **Technology**: Python/FastAPI with async processing
- **Architecture**:
  ```python
  class EnhancedAIOrchestrator:
      - Detection queue management
      - Multi-worker processing
      - Service coordination
      - Real-time broadcasting
      - Performance monitoring
  ```

#### Threat Detector Service
- **Purpose**: Multi-factor threat analysis and alert generation with machine learning models
- **Technology**: Python/FastAPI with PyTorch, YOLOv8, MediaPipe, and EasyOCR
- **7-Factor Analysis** (50% ML-based):
  1. **Object Type Analysis** (15% weight): Base threat level by detection class
  2. **Weapon Detection** (30% weight): **YOLOv8** ML model for firearms, knives, threats
  3. **Behavior Analysis** (20% weight): Movement patterns, dwell time, suspicious activity
  4. **Context Analysis** (10% weight): Time of day, location, zone violations, crowd density
  5. **Historical Analysis** (5% weight): Recent threats in area, pattern matching
  6. **Face Recognition** (10% weight): **MediaPipe/InsightFace** for watchlist, unknown persons
  7. **Vehicle/Plate Analysis** (10% weight): **EasyOCR** for license plates, stolen vehicles

**AI Models**:
- **YOLOv8** (Ultralytics): Real-time weapon and object detection with GPU acceleration
- **MediaPipe**: Fast face detection with facial landmarks (default)
- **InsightFace**: Advanced face recognition with embeddings, age/gender (optional)
- **EasyOCR**: Multi-language license plate OCR with pattern matching
- **Fallback Mechanisms**: Heuristic-based detection when ML models unavailable

#### Object Tracker (Planned)
- **Purpose**: Multi-camera object correlation and tracking
- **Technology**: Rust for high-performance processing
- **Features**:
  - Cross-camera object correlation
  - Trajectory prediction
  - Re-identification (ReID)
  - Global tracking state management

### 3. Data Layer

#### TimescaleDB
- **Purpose**: Time-series data storage for events and analytics
- **Schema**:
  ```sql
  CREATE TABLE intelligence_results (
      detection_id TEXT PRIMARY KEY,
      camera_id TEXT NOT NULL,
      timestamp TIMESTAMPTZ NOT NULL,
      threat_score FLOAT,
      threat_level TEXT,
      ai_models_used TEXT[],
      insights JSONB,
      processing_time_ms FLOAT
  );
  ```

#### Redis
- **Purpose**: High-performance caching and real-time data
- **Usage**:
  - Session management
  - Real-time analytics cache
  - Pub/sub for live updates
  - Rate limiting and throttling

#### Qdrant Vector Database
- **Purpose**: Vector embeddings for similarity search
- **Usage**:
  - Face recognition embeddings
  - Behavioral pattern vectors
  - Similarity-based search
  - Clustering and analysis

#### MinIO Object Storage
- **Purpose**: S3-compatible object storage for media files
- **Usage**:
  - Video recordings
  - Image snapshots
  - Model artifacts
  - Backup storage

### 4. Presentation Layer

#### Real-time Dashboard
- **Technology**: Next.js 14 with TypeScript
- **Features**:
  - Real-time camera feeds
  - Threat visualization
  - Alert management
  - System monitoring
  - Responsive design

#### Mobile Application (Planned)
- **Technology**: React Native
- **Features**:
  - Push notifications
  - Remote monitoring
  - Alert acknowledgment
  - Quick actions

## Data Flow Architecture

### 1. Detection Pipeline

```
Camera Feed → Frigate Plus → Object Detection → Event Generation
     ↓
Enhanced AI Orchestrator → Detection Queue → Worker Processing
     ↓
Threat Detector → Multi-factor Analysis → Threat Score
     ↓
Alert Manager → Priority Assessment → Notification System
     ↓
Database Storage ← Cache Update ← Real-time Broadcast
```

### 2. Real-time Processing

```python
# Async processing pipeline with AI models
async def process_detection(detection_event):
    # Step 1: Run parallel AI model analysis
    weapon_task = asyncio.create_task(
        threat_detector.weapon_detector.detect_weapon(frame_data)
    )
    face_task = asyncio.create_task(
        threat_detector.face_detector.detect_faces(frame_data)
    )
    plate_task = asyncio.create_task(
        threat_detector.plate_recognizer.recognize_plate(frame_data)
    )

    # Wait for all models to complete
    weapon_score, faces, plates = await asyncio.gather(
        weapon_task, face_task, plate_task
    )

    # Step 2: Comprehensive 7-factor threat analysis
    threat_analysis = await threat_detector.analyze(
        detection_event,
        weapon_score=weapon_score,
        faces=faces,
        plates=plates
    )

    # Step 3: Generate insights
    insights = await generate_insights(detection_event, threat_analysis)

    # Step 4: Store results with model metadata
    await store_intelligence_result(insights)

    # Step 5: Broadcast real-time updates
    await broadcast_to_clients(insights)
```

### 3. Service Communication

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│ AI Orchestrator │ ←──────────────→ │ Threat Detector │
└─────────────────┘                  └─────────────────┘
         │                                    │
         │ WebSocket                          │ Database
         ↓                                    ↓
┌─────────────────┐                  ┌─────────────────┐
│    Dashboard    │                  │   TimescaleDB   │
└─────────────────┘                  └─────────────────┘
```

### 4. AI Detection Endpoints

The Threat Detector service provides specialized endpoints for each AI model:

```
POST /analyze                    # Comprehensive 7-factor threat analysis
POST /detect/faces              # Face detection (MediaPipe/InsightFace)
POST /detect/plates             # License plate recognition (EasyOCR)
POST /detect/comprehensive      # All AI models in single call
GET  /models/info              # Check model status and capabilities
GET  /stats                    # Threat detection statistics
GET  /history                  # Historical threat data
```

**Model Selection Strategy**:
```python
# Automatic model selection based on detection type
if detection_type == "person":
    # Run weapon + face detection
    weapon_score = await weapon_detector.detect(frame)
    faces = await face_detector.detect(frame)
elif detection_type == "vehicle":
    # Run plate recognition
    plates = await plate_recognizer.recognize(frame)
```

## Scalability Architecture

### Horizontal Scaling

#### Microservices Design
- Each service can be scaled independently
- Load balancing across service instances
- Database connection pooling
- Stateless service design

#### Container Orchestration
```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threat-detector
spec:
  replicas: 3
  selector:
    matchLabels:
      app: threat-detector
  template:
    spec:
      containers:
      - name: threat-detector
        image: ai-security/threat-detector:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
```

### Performance Optimization

#### GPU Acceleration
- TensorRT model optimization
- CUDA stream processing
- Multi-GPU support
- Memory management

#### Caching Strategy
```python
# Multi-level caching
class CacheStrategy:
    - L1: In-memory cache (Redis)
    - L2: Database query cache
    - L3: Model inference cache
    - L4: Static asset cache (CDN)
```

#### Database Optimization
- Time-series partitioning
- Index optimization
- Connection pooling
- Read replicas

## Security Architecture

### Network Security
- Service mesh with mTLS
- Network segmentation
- Firewall rules
- VPN access

### Data Security
- Encryption at rest
- Encryption in transit
- Key management
- Access control

### Authentication & Authorization
```python
# JWT-based authentication
class SecurityMiddleware:
    - Token validation
    - Role-based access control (RBAC)
    - API rate limiting
    - Audit logging
```

## Monitoring & Observability

### Metrics Collection
```yaml
# Prometheus metrics
- System metrics (CPU, memory, GPU)
- Application metrics (latency, throughput)
- Business metrics (threat detection rate)
- Custom metrics (model accuracy)
```

### Logging Strategy
```python
# Structured logging
{
    "timestamp": "2024-01-01T12:00:00Z",
    "level": "INFO",
    "service": "threat-detector",
    "trace_id": "abc123",
    "message": "Threat detected",
    "metadata": {
        "camera_id": "entrance_01",
        "threat_score": 0.85,
        "threat_level": "HIGH"
    }
}
```

### Distributed Tracing
- OpenTelemetry integration
- Request correlation
- Performance profiling
- Error tracking

## Deployment Architecture

### Development Environment
```bash
# Docker Compose for local development
docker-compose -f docker/compose/docker-compose.yml up -d
```

### Production Environment
```bash
# Kubernetes deployment
kubectl apply -f infrastructure/kubernetes/
```

### CI/CD Pipeline
```yaml
# GitHub Actions workflow
- Build and test
- Security scanning
- Container image build
- Deployment to staging
- Integration tests
- Production deployment
```

## Future Architecture Considerations

### Event Streaming (Phase 3)
```
Apache Kafka → Apache Flink → Real-time Analytics
     ↓              ↓              ↓
Event Store → Stream Processing → Materialized Views
```

### Machine Learning Pipeline
```
Data Collection → Feature Engineering → Model Training
     ↓                    ↓                 ↓
Model Registry → A/B Testing → Production Deployment
```

### Edge Computing
```
Edge Devices → Local Processing → Cloud Aggregation
     ↓              ↓                 ↓
Reduced Latency → Bandwidth Savings → Centralized Intelligence
```

## Performance Characteristics

### Current Benchmarks
- **Object Detection (YOLOv8)**: ~50-100ms per frame (GPU) / 200-500ms (CPU)
- **Face Detection (MediaPipe)**: ~30-50ms per frame
- **License Plate OCR (EasyOCR)**: ~300-400ms per plate region
- **Comprehensive 7-Factor Analysis**: <500ms average (parallel processing)
- **Alert Generation**: <500ms for critical threats
- **Dashboard Load**: <2 seconds
- **Concurrent Cameras**: 50+ feeds
- **API Throughput**: 100 requests/minute per service instance

### AI Model Performance
- **YOLOv8 Weapon Detection**:
  - Precision: ~90% (on test dataset)
  - Recall: ~85%
  - GPU acceleration: 5-10x faster than CPU
- **MediaPipe Face Detection**:
  - Detection rate: >95% for frontal faces
  - Processing speed: Real-time (30 FPS on GPU)
- **EasyOCR Plate Recognition**:
  - Accuracy: ~85-90% (varies by lighting/angle)
  - Multi-language support
  - GPU acceleration supported

### Scalability Targets
- **Horizontal Scaling**: 10x current capacity
- **Geographic Distribution**: Multi-region deployment
- **High Availability**: 99.9% uptime SLA
- **Disaster Recovery**: <1 hour RTO, <15 minutes RPO

This architecture provides a solid foundation for the AI Security Lab v4.0 system, with clear separation of concerns, scalability considerations, and production-ready design patterns.
