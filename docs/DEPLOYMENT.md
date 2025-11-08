# AI Security Lab v4.0 - Deployment Guide

Complete guide for deploying the AI Security Lab in production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Monitoring](#monitoring)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling](#scaling)
8. [Troubleshooting](#troubleshooting)
9. [Security](#security)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 8 cores
- RAM: 16 GB
- Storage: 100 GB SSD
- OS: Linux (Ubuntu 20.04+ recommended)

**Recommended:**
- CPU: 16+ cores
- RAM: 32+ GB
- Storage: 500 GB NVMe SSD
- GPU: NVIDIA with 8GB+ VRAM (for ML acceleration)
- OS: Ubuntu 22.04 LTS

### Software Dependencies

```bash
# Docker (20.10+)
curl -fsSL https://get.docker.com | sh

# Docker Compose (2.0+)
sudo apt-get install docker-compose-plugin

# Git
sudo apt-get install git

# Optional: NVIDIA Docker (for GPU support)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/shift7az/ai-security-lab-v4.git
cd ai-security-lab-v4
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env.production

# Edit configuration (IMPORTANT: Change all passwords!)
nano .env.production
```

**Required Environment Variables:**

```bash
# Database
DATABASE_PASSWORD=your-secure-password-here

# Redis
REDIS_PASSWORD=your-redis-password-here

# MinIO
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-minimum-32-characters-long

# Frigate (if using external Frigate instance)
FRIGATE_API_KEY=your-frigate-api-key

# Grafana
GRAFANA_ADMIN_PASSWORD=your-grafana-password

# API
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Start all services
./scripts/deploy.sh start
```

### 4. Verify Deployment

```bash
# Check service status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs
```

**Access Points:**
- Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

---

## Configuration

### Service Configuration

#### TimescaleDB

Location: `docker/compose/docker-compose.prod.yml`

```yaml
timescaledb:
  environment:
    POSTGRES_DB: security_events
    POSTGRES_USER: security
    POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
```

#### Redis

```yaml
redis-stack:
  environment:
    REDIS_ARGS: "--requirepass ${REDIS_PASSWORD}"
```

#### AI Orchestrator

Location: `services/core/ai-orchestrator/.env`

```bash
# Database Connection
DATABASE_HOST=timescaledb
DATABASE_PORT=5432
DATABASE_NAME=security_events

# Redis Connection  
REDIS_HOST=redis-stack
REDIS_PORT=6379

# Performance Tuning
MAX_CONCURRENT_ANALYSES=10
DETECTION_QUEUE_SIZE=1000
WORKER_COUNT=5

# GPU Settings
GPU_ENABLED=true
GPU_DEVICE_ID=0
BATCH_SIZE=8
```

### Network Configuration

The system uses a custom bridge network (`ai-security-network`) with subnet `172.20.0.0/16`.

To modify:
1. Edit `docker/compose/docker-compose.prod.yml`
2. Update the `networks` section
3. Restart services

---

## Deployment

### Production Deployment

#### Using Deployment Script

```bash
# Start all services
./scripts/deploy.sh start

# Stop all services
./scripts/deploy.sh stop

# Restart all services
./scripts/deploy.sh restart

# View specific service logs
./scripts/deploy.sh logs ai-orchestrator

# Check system status
./scripts/deploy.sh status
```

#### Manual Docker Compose

```bash
# Start services
docker-compose -f docker/compose/docker-compose.prod.yml \
  --env-file .env.production up -d

# Stop services
docker-compose -f docker/compose/docker-compose.prod.yml down

# View logs
docker-compose -f docker/compose/docker-compose.prod.yml logs -f
```

### Database Migrations

```bash
# Run migrations automatically on startup
# Or manually:
./scripts/deploy.sh migrate
```

### Initial Setup

After first deployment:

1. **Create Admin User:**
```bash
docker exec -it ai-security-orchestrator python -c "
from src.services.auth_service import AuthService
from src.services.database import DatabaseService
import asyncio

async def create_admin():
    db = DatabaseService('timescaledb', 5432, 'security_events', 'security', 'password')
    await db.connect()
    auth = AuthService(db, 'your-jwt-secret')
    user = await auth.create_user('admin', 'admin@example.com', 'admin123', 'admin')
    print(f'Created admin user: {user.username}')
    await db.disconnect()

asyncio.run(create_admin())
"
```

2. **Seed Test Data (Development Only):**
```bash
docker exec -it ai-security-orchestrator python -m src.database.seed
```

3. **Configure Cameras:**
- Access dashboard at http://localhost:3000
- Login with admin credentials
- Navigate to Settings > Cameras
- Add your camera streams

---

## Monitoring

### Grafana Dashboards

Access: http://localhost:3001

**Default Login:**
- Username: admin
- Password: (from GRAFANA_ADMIN_PASSWORD)

**Pre-configured Dashboards:**
- System Overview
- Threat Analytics
- Resource Monitoring
- API Performance

### Prometheus Metrics

Access: http://localhost:9090

**Available Metrics:**
- `threat_detections_total` - Total threat detections
- `cpu_usage_percent` - CPU utilization
- `memory_usage_percent` - Memory usage
- `gpu_usage_percent` - GPU utilization
- `http_requests_total` - API request count
- `database_connections_active` - Active DB connections

### Health Checks

```bash
# Check AI Orchestrator health
curl http://localhost:8000/health

# Check Dashboard health
curl http://localhost:3000

# Check all services
./scripts/deploy.sh status
```

---

## Backup & Recovery

### Automated Backups

```bash
# Create backup
./scripts/deploy.sh backup

# Backups are stored in ./backups/
# Format: database_YYYYMMDD_HHMMSS.sql.gz
```

### Manual Backup

```bash
# Backup database
docker exec ai-security-timescaledb pg_dump -U security security_events \
  > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql
```

### Restore from Backup

```bash
# Using deployment script
./scripts/deploy.sh restore backups/database_20250107_120000.sql.gz

# Manual restore
gunzip -c backup.sql.gz | docker exec -i ai-security-timescaledb \
  psql -U security security_events
```

### Backup Schedule Recommendation

Use cron for automated backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/ai-security-lab-v4 && ./scripts/deploy.sh backup
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale AI Orchestrator to 3 instances
./scripts/deploy.sh scale ai-orchestrator 3

# Scale Threat Detector to 2 instances
./scripts/deploy.sh scale threat-detector 2
```

### Vertical Scaling

Edit resource limits in `docker/compose/docker-compose.prod.yml`:

```yaml
ai-orchestrator:
  deploy:
    resources:
      limits:
        cpus: '8'      # Increase CPU
        memory: 8G     # Increase memory
```

### Load Balancing

For production with multiple instances, add Nginx configuration:

```nginx
upstream ai_orchestrator {
    least_conn;
    server ai-orchestrator-1:8000;
    server ai-orchestrator-2:8000;
    server ai-orchestrator-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://ai_orchestrator;
    }
}
```

---

## Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check Docker service
sudo systemctl status docker

# Check logs
./scripts/deploy.sh logs

# Check disk space
df -h

# Check memory
free -h
```

#### Database Connection Errors

```bash
# Verify database is running
docker ps | grep timescaledb

# Check database logs
docker logs ai-security-timescaledb

# Test connection
docker exec ai-security-timescaledb pg_isready -U security

# Restart database
docker restart ai-security-timescaledb
```

#### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce resource usage
# Edit docker-compose.prod.yml and lower memory limits

# Restart services
./scripts/deploy.sh restart
```

#### Performance Issues

```bash
# Check system resources
htop

# Monitor database queries
docker exec ai-security-timescaledb psql -U security -d security_events \
  -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis memory
docker exec ai-security-redis redis-cli INFO memory
```

### Debug Mode

Enable debug logging:

```bash
# Edit .env.production
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
./scripts/deploy.sh restart
```

---

## Security

### Best Practices

1. **Change Default Passwords**
   - Update all passwords in `.env.production`
   - Use strong, unique passwords (20+ characters)
   - Consider using a password manager

2. **Enable HTTPS**
   - Configure SSL certificates in Nginx
   - Use Let's Encrypt for free certificates
   - Redirect HTTP to HTTPS

3. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

4. **Regular Updates**
   ```bash
   # Update system
   sudo apt-get update && sudo apt-get upgrade

   # Update containers
   ./scripts/deploy.sh update
   ```

5. **Backup Encryption**
   ```bash
   # Encrypt backups
   gpg --symmetric --cipher-algo AES256 backup.sql.gz
   ```

### Security Checklist

- [ ] Changed all default passwords
- [ ] Configured firewall rules
- [ ] Enabled HTTPS with valid certificates
- [ ] Set up automated backups
- [ ] Configured log rotation
- [ ] Limited database access
- [ ] Enabled audit logging
- [ ] Regular security updates
- [ ] Monitored system logs
- [ ] Restricted API access

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/shift7az/ai-security-lab-v4/issues
- Documentation: https://github.com/shift7az/ai-security-lab-v4/tree/master/docs

---

**Version:** 4.0.0  
**Last Updated:** January 2025
