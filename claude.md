# AI Security Lab v4.0 - Claude Code Context

## Project Overview

AI Security Lab v4.0 is a production-ready, enterprise-grade AI-powered surveillance system providing real-time threat detection, behavioral analysis, and automated security monitoring. The system processes multiple camera feeds simultaneously using advanced AI models including YOLOv8 for weapon detection, MediaPipe/InsightFace for face recognition, EasyOCR for license plate reading, and rule-based behavior analysis.

**Status**: 100% Complete (Production Ready)
**Repository**: https://github.com/shift7az/ai-security-lab-v4
**AI Models**: YOLOv8, MediaPipe, EasyOCR, InsightFace (optional)

## Technology Stack

### Backend
- **FastAPI**: Async Python web framework for REST APIs
- **TimescaleDB**: PostgreSQL with time-series extensions for event storage
- **Redis Stack**: Caching and real-time data buffering
- **Socket.IO**: WebSocket real-time communication
- **JWT**: HS256 token-based authentication
- **Pydantic**: Data validation and serialization
- **AsyncPG**: Async PostgreSQL driver

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Strict mode with comprehensive type safety
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization charts
- **React Query**: Server state management
- **Socket.IO Client**: Real-time updates

### Infrastructure
- **Docker Compose**: Container orchestration
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Tempo**: Distributed tracing
- **MinIO**: Object storage for media files
- **Nginx**: Reverse proxy (production)

### AI Models
- **YOLOv8** (Ultralytics): Weapon and object detection (30% threat weight)
- **MediaPipe**: Fast face detection with landmarks (10% threat weight)
- **InsightFace** (Optional): Advanced face recognition with age/gender
- **EasyOCR**: License plate recognition and OCR (10% threat weight)
- **Rule-based Behavior**: Behavioral pattern analysis (20% threat weight)

## Project Structure

```
ai-security-lab-v4/
├── services/
│   ├── core/
│   │   └── ai-orchestrator/          # Main backend service
│   │       ├── src/
│   │       │   ├── api/              # REST API endpoints
│   │       │   │   ├── auth.py       # Authentication endpoints
│   │       │   │   ├── dashboard.py  # Dashboard data endpoints
│   │       │   │   └── settings.py   # Settings management
│   │       │   ├── core/             # Core business logic
│   │       │   │   └── enhanced_orchestrator.py
│   │       │   ├── services/         # Service layer
│   │       │   │   ├── auth_service.py
│   │       │   │   ├── database.py
│   │       │   │   ├── cache.py
│   │       │   │   ├── frigate_client.py
│   │       │   │   └── threat_detector_client.py
│   │       │   ├── models/           # Pydantic models
│   │       │   ├── database/         # DB migrations and seeds
│   │       │   └── config/           # Configuration
│   │       └── tests/                # Backend tests
│   ├── ui/
│   │   └── dashboard/                # Next.js frontend
│   │       ├── app/                  # App Router pages
│   │       ├── components/           # React components
│   │       │   ├── cameras/          # Camera grid components
│   │       │   ├── alerts/           # Alert management
│   │       │   ├── threats/          # Threat overview
│   │       │   ├── system/           # System status
│   │       │   ├── intelligence/     # Intelligence timeline
│   │       │   └── charts/           # Data visualization
│   │       ├── hooks/                # Custom React hooks
│   │       └── types/                # TypeScript types
│   └── intelligence/
│       └── threat-detector/          # Threat detection service
├── docker/compose/                   # Docker Compose files
├── config/                           # Service configurations
├── tests/                            # Integration tests
├── scripts/                          # Deployment and utility scripts
└── docs/                             # Documentation

```

## Key Services

### 1. AI Orchestrator (Port 8000)
Main backend service coordinating all AI services and providing the REST API.

**Key Files**:
- `services/core/ai-orchestrator/src/core/enhanced_orchestrator.py`: Core orchestration logic
- `services/core/ai-orchestrator/src/api/`: FastAPI endpoint definitions
- `services/core/ai-orchestrator/src/services/`: Service layer (DB, cache, clients)

**Endpoints**:
- `/api/auth/*`: Authentication and user management
- `/api/dashboard/*`: Dashboard data (cameras, alerts, timeline, stats)
- `/api/settings/*`: Runtime configuration management
- `/health`: Health check
- `/process-frame`: Process camera frames
- `/detections/{camera_id}`: Get detections for camera

### 2. Dashboard (Port 3000)
Next.js 14 real-time dashboard with 19 React components.

**Key Components**:
- `CameraGrid`: Live camera feed monitoring
- `ThreatOverview`: Aggregated threat statistics
- `AlertPanel`: Alert management with ACK/resolve
- `SystemStatus`: Service health monitoring
- `IntelligenceTimeline`: Chronological event feed
- `ThreatTrendsChart`, `CameraActivityChart`, `AlertDistributionChart`: Data visualizations

**Real-time Features**:
- Socket.IO integration with auto-reconnect
- 5 WebSocket event types (threats, alerts, system, camera updates)
- Optimistic UI updates

### 3. Threat Detector (Port 8001)
Dedicated service for comprehensive multi-factor threat analysis using multiple AI models.

**7-Factor Threat Scoring System**:
1. **Object Type Analysis** (15% weight) - Base threat by object class
2. **Weapon Detection** (30% weight) - YOLOv8 ML model for firearms, knives, threats
3. **Behavior Analysis** (20% weight) - Movement patterns, dwell time, suspicious activity
4. **Context Analysis** (10% weight) - Time, location, crowd density
5. **Historical Analysis** (5% weight) - Recent threats in area
6. **Face Recognition** (10% weight) - MediaPipe/InsightFace for watchlist, unknown persons
7. **Vehicle/Plate Analysis** (10% weight) - EasyOCR for license plates, stolen vehicles

**AI Models**:
- YOLOv8: Weapon and threat object detection
- MediaPipe: Face detection with landmarks
- InsightFace: Face recognition with embeddings (optional)
- EasyOCR: License plate OCR and recognition

**Endpoints**:
- `POST /analyze`: Full threat analysis with all 7 factors
- `POST /detect/faces`: Face detection only
- `POST /detect/plates`: License plate recognition only
- `POST /detect/comprehensive`: Run ALL models at once
- `GET /models/info`: Check model status and configuration
- `GET /history`: Threat analysis history
- `GET /stats`: Threat statistics

## Development Workflow

### Starting the Development Environment

```bash
# Start all services
make dev

# Or manually
docker-compose -f docker/compose/docker-compose.yml up -d
```

### Backend Development

```bash
cd services/core/ai-orchestrator

# Install dependencies (if developing locally)
pip install -r requirements.txt

# Run tests
pytest tests/

# Format code
ruff check --fix .
black .
```

### Frontend Development

```bash
cd services/ui/dashboard

# Install dependencies
npm install

# Start dev server (standalone)
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint
```

## Common Tasks

### Adding a New API Endpoint

1. Add endpoint to `services/core/ai-orchestrator/src/api/`
2. Add service logic to `services/core/ai-orchestrator/src/services/`
3. Add Pydantic models to `services/core/ai-orchestrator/src/models/`
4. Add tests to `services/core/ai-orchestrator/tests/`

### Adding a New Dashboard Component

1. Create component in `services/ui/dashboard/components/`
2. Add TypeScript types to `services/ui/dashboard/types/`
3. Use React Query for data fetching
4. Add Socket.IO listeners for real-time updates

### Database Changes

1. Create migration in `services/core/ai-orchestrator/src/database/migrations.py`
2. Run migration: `python -m src.database.migrations`
3. Update models in `src/models/`

## Coding Conventions

### Python
- **Style**: PEP 8 compliant, Black formatted
- **Type hints**: Required for all function signatures
- **Docstrings**: Google-style for all public functions/classes
- **Async**: Use async/await for I/O operations
- **Error handling**: Use custom exceptions, log errors
- **Imports**: Grouped (stdlib, third-party, local)

Example:
```python
async def process_detection(
    camera_id: str,
    detection: Detection,
    db: Database
) -> ThreatAnalysis:
    """Process a detection and analyze for threats.

    Args:
        camera_id: Unique camera identifier
        detection: Detection object from AI model
        db: Database connection

    Returns:
        ThreatAnalysis with threat level and factors

    Raises:
        DatabaseError: If database operation fails
    """
    pass
```

### TypeScript
- **Style**: ESLint + Prettier configured
- **Types**: Strict mode, no `any` types
- **Components**: Functional components with hooks
- **Props**: Define interfaces for all component props
- **State**: Use React Query for server state, useState for local state
- **Error handling**: Use try/catch with error boundaries

Example:
```typescript
interface CameraGridProps {
  cameras: Camera[]
  onCameraSelect: (cameraId: string) => void
}

export function CameraGrid({ cameras, onCameraSelect }: CameraGridProps) {
  // Component implementation
}
```

## Database Schema

### Key Tables
- `cameras`: Camera configuration and metadata
- `detections`: All AI model detections
- `threats`: Threat analysis results
- `alerts`: User-facing alerts
- `events`: System events and intelligence timeline
- `users`: Authentication and authorization
- `settings`: Runtime configuration

### Indexes
15 strategic indexes including composite, partial, and GIN indexes for optimal query performance.

### TimescaleDB Features
- Hypertables for time-series data
- Continuous aggregates for statistics
- Retention policies (30-90 days)

## Authentication & Authorization

### JWT Tokens
- **Algorithm**: HS256
- **Access token**: 30 minutes expiry
- **Refresh token**: 7 days expiry
- **Secret**: From `JWT_SECRET_KEY` env variable (min 32 chars)

### Roles
- **Admin**: Full system access, user management
- **Operator**: Acknowledge alerts, view all data
- **Viewer**: Read-only access

### Protected Endpoints
Use `get_current_user` dependency for authentication.
Use `require_role` decorator for authorization.

## Testing Strategy

### Backend Tests (pytest)
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database integration tests
- Authentication flow tests

Run: `pytest tests/` or `make test`

### Frontend Tests
- Component tests (future: Vitest + React Testing Library)
- E2E tests (future: Playwright)

### Manual Testing
Run comprehensive test suite:
```bash
python tests/run_all_tests.py
```

## Deployment

### Development
```bash
make dev
```

### Production
```bash
./scripts/deploy.sh start

# Other commands
./scripts/deploy.sh status
./scripts/deploy.sh logs
./scripts/deploy.sh backup
./scripts/deploy.sh scale ai-orchestrator 3
```

### Environment Variables

Key variables in `.env` (copy from `.env.example`):
- `DATABASE_PASSWORD`: PostgreSQL password
- `REDIS_PASSWORD`: Redis password
- `JWT_SECRET_KEY`: JWT signing key (min 32 chars)
- `FRIGATE_API_KEY`: Frigate integration key
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

## Performance Considerations

### Database
- Use connection pooling (AsyncPG pool)
- Use prepared statements and parameterized queries
- Leverage continuous aggregates for statistics
- Use Redis for frequently accessed data
- Monitor query performance with Prometheus

### Backend
- Use async/await for all I/O
- Implement caching for expensive operations
- Use background tasks for non-critical operations
- Rate limit API endpoints if needed

### Frontend
- Use React Query for automatic caching
- Implement code splitting (Next.js automatic)
- Lazy load heavy components
- Optimize re-renders with memo/useMemo
- Use WebSocket only for real-time data

## Monitoring & Observability

### Metrics (Prometheus)
- Request latency and throughput
- Error rates
- Database connection pool
- Cache hit rates
- Custom business metrics

### Dashboards (Grafana)
Access: http://localhost:3001
- System health overview
- API performance
- Database statistics
- Threat detection analytics

### Logs
- Structured JSON logging
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Request ID tracking for distributed tracing

## Important Files

- **README.md**: Project overview and quick start
- **PROJECT_SUMMARY.md**: Detailed project documentation
- **CONTRIBUTING.md**: Contribution guidelines
- **Makefile**: Common development tasks
- **docker-compose.yml**: Development environment
- **docker-compose.prod.yml**: Production environment
- **.env.example**: Template for environment variables

## Common Issues & Solutions

### Database Connection Issues
- Ensure TimescaleDB is running: `docker ps`
- Check credentials in `.env`
- Verify network connectivity: `docker network ls`

### Frontend Build Errors
- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run type-check`

### Authentication Issues
- Verify JWT_SECRET_KEY is set and minimum 32 characters
- Check token expiry times
- Clear browser cookies/localStorage

## External Dependencies

### Required Services
- **Frigate**: NVR with object detection (optional but recommended)
- **TimescaleDB**: Time-series database (required)
- **Redis Stack**: Caching and real-time data (required)

### Optional Services
- **MinIO**: Object storage for media
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Tempo**: Distributed tracing

## Security Notes

- Never commit secrets to git
- Use environment variables for all credentials
- JWT secrets must be strong (32+ chars)
- Passwords hashed with bcrypt (12 rounds)
- Parameterized queries prevent SQL injection
- CORS configured for production domains
- Rate limiting recommended for production
- HTTPS required for production (Nginx configured)

## Future Enhancements

Planned features (post v4.0):
- Mobile app (iOS/Android)
- Advanced face recognition
- License plate recognition
- SMS/Push notifications
- Multi-tenant support
- Kubernetes deployment
- GraphQL API option
- Advanced reporting engine

## Getting Help

- Check documentation in `docs/`
- Review tests for usage examples
- Check Makefile for available commands
- Review API docs: http://localhost:8000/docs (when running)
- Check logs: `make logs` or `docker-compose logs`

## Related Documentation

- **USER_MANUAL.md**: End-user guide
- **DEPLOYMENT.md**: Production deployment details
- **ARCHITECTURE.md**: System architecture deep-dive
- **API.md**: Complete API documentation
- **DASHBOARD_IMPLEMENTATION.md**: Frontend component guide
