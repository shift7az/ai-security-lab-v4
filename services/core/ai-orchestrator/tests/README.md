# Tests for AI Security Lab v4.0 AI Orchestrator

## Test Suite Overview

Comprehensive test coverage for the AI Orchestrator service.

## Running Tests

### Setup

```bash
# Activate virtual environment
cd services/core/ai-orchestrator
source venv/bin/activate

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database_service.py

# Run specific test
pytest tests/test_database_service.py::TestDatabaseService::test_connection
```

## Test Files

### `test_database_service.py` (130 lines)
Tests for DatabaseService including:
- Connection and health checks
- Query execution (execute, fetch_one, fetch_all)
- Domain-specific queries (cameras, alerts, threats)
- Statistics and trend calculations
- Transaction support
- Connection pool stats

### `test_cache_service.py` (100 lines)
Tests for CacheService including:
- Connection and health checks
- Basic operations (get, set, delete, exists)
- TTL management
- JSON operations
- Key expiration

### `test_api_endpoints.py` (40 lines)
Smoke tests for API endpoints including:
- Health endpoint
- Dashboard overview
- Cameras endpoint
- Settings endpoints

### `conftest.py` (75 lines)
Pytest fixtures including:
- Event loop for async tests
- Settings fixture
- Database service fixture
- Cache service fixture
- Test data cleanup

## Test Coverage

Current test coverage focuses on:
- ✅ Service layer (Database, Cache)
- ✅ API endpoints (smoke tests)
- ✅ Basic functionality

Future additions:
- [ ] Model validation tests
- [ ] Enhanced orchestrator tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Frontend component tests

## Requirements

Tests require:
- PostgreSQL/TimescaleDB running
- Redis running
- Database schema applied (`python scripts/migrate.py up`)
- Test data seeded (optional)

## CI/CD Integration

Add to GitHub Actions:
```yaml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml
```

## Notes

- Async tests use `pytest-asyncio`
- Database tests use real connection (not mocked)
- Cache tests use real Redis (not mocked)
- API tests are basic smoke tests
- More comprehensive tests can be added incrementally
