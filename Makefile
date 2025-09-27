# ============================================================================
# AI Security Lab v4.0 - Management Makefile
# ============================================================================

.PHONY: help dev prod gpu-test train-model backup restore monitoring logs clean

# Default target
help:
	@echo "AI Security Lab v4.0 - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          Start development environment"
	@echo "  make prod         Start production environment"
	@echo "  make down         Stop all services"
	@echo "  make restart      Restart all services"
	@echo ""
	@echo "GPU & Hardware:"
	@echo "  make gpu-test     Test GPU availability and performance"
	@echo "  make gpu-info     Show GPU information"
	@echo "  make nvidia-smi  Show NVIDIA GPU status"
	@echo ""
	@echo "AI & Machine Learning:"
	@echo "  make train-model  Train custom models"
	@echo "  make test-models  Test model accuracy"
	@echo "  make update-models Update AI models"
	@echo ""
	@echo "Data Management:"
	@echo "  make backup       Create full system backup"
	@echo "  make restore      Restore from backup"
	@echo "  make clean-data   Clean old data files"
	@echo ""
	@echo "Monitoring & Logs:"
	@echo "  make monitoring   Open monitoring dashboards"
	@echo "  make logs         Show all service logs"
	@echo "  make log-follow   Follow logs for all services"
	@echo "  make log-frigate  Show Frigate logs only"
	@echo ""
	@echo "Maintenance:"
	@echo "  make health       Check system health"
	@echo "  make status       Show service status"
	@echo "  make clean        Clean Docker system"
	@echo "  make prune        Remove unused Docker resources"
	@echo ""
	@echo "Database:"
	@echo "  make db-init      Initialize databases"
	@echo "  make db-reset     Reset all databases (DANGER)"
	@echo "  make db-backup    Backup databases"
	@echo ""

# ============================================================================
# ENVIRONMENT MANAGEMENT
# ============================================================================

dev:
	@echo "Starting AI Security Lab v4.0 (Development Mode)..."
	docker-compose --env-file .env -f docker/compose/docker-compose.yml up -d
	@echo "Development environment started!"
	@echo "Dashboard: http://localhost:3001"
	@echo "Frigate:   http://localhost:5000"
	@echo "Grafana:   http://localhost:3000"
	@echo "MinIO:     http://localhost:9001"

prod:
	@echo "Starting AI Security Lab v4.0 (Production Mode)..."
	docker-compose --env-file .env -f docker/compose/docker-compose.yml -f docker/compose/docker-compose.prod.yml up -d
	@echo "Production environment started!"

down:
	@echo "Stopping all services..."
	docker-compose -f docker/compose/docker-compose.yml down

restart:
	@echo "Restarting all services..."
	docker-compose -f docker/compose/docker-compose.yml restart

# ============================================================================
# GPU & HARDWARE
# ============================================================================

gpu-test:
	@echo "Testing GPU availability..."
	@nvidia-smi || echo "NVIDIA GPU not found"
	@echo "Testing CUDA..."
	@docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi || echo "CUDA test failed"
	@echo "Testing GPU memory..."
	@docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits

gpu-info:
	@echo "GPU Information:"
	@nvidia-smi -L
	@nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv

nvidia-smi:
	nvidia-smi

# ============================================================================
# AI & MACHINE LEARNING
# ============================================================================

train-model:
	@echo "Training custom AI models..."
	@docker-compose -f docker/compose/docker-compose.yml run --rm ai-orchestrator python ml-models/training/train_custom_models.py

test-models:
	@echo "Testing model accuracy..."
	@docker-compose -f docker/compose/docker-compose.yml run --rm ai-orchestrator python ml-models/evaluation/test_models.py

update-models:
	@echo "Updating AI models..."
	@docker-compose -f docker/compose/docker-compose.yml run --rm ai-orchestrator python tools/update_models.py

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

backup:
	@echo "Creating full system backup..."
	@mkdir -p backups/$$(date +%Y%m%d_%H%M%S)
	@echo "Backing up databases..."
	@docker-compose -f docker/compose/docker-compose.yml exec timescaledb pg_dump -U security security_events > backups/$$(date +%Y%m%d_%H%M%S)/security_events.sql
	@echo "Backing up configurations..."
	@cp -r config backups/$$(date +%Y%m%d_%H%M%S)/
	@echo "Backing up media (this may take a while)..."
	@docker run --rm -v ai-security-lab-v4_frigate-media:/source -v $$(pwd)/backups/$$(date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/media.tar.gz -C /source .
	@echo "Backup completed: backups/$$(date +%Y%m%d_%H%M%S)/"

restore:
	@echo "WARNING: This will overwrite current data!"
	@read -p "Enter backup directory name: " backup_dir; \
	if [ -d "backups/$$backup_dir" ]; then \
		echo "Restoring from backups/$$backup_dir..."; \
		docker-compose -f docker/compose/docker-compose.yml down; \
		docker-compose -f docker/compose/docker-compose.yml exec timescaledb psql -U security -d security_events -f backups/$$backup_dir/security_events.sql; \
		echo "Restore completed!"; \
	else \
		echo "Backup directory not found: backups/$$backup_dir"; \
	fi

clean-data:
	@echo "Cleaning old data files..."
	@find data/ -type f -name "*.log" -mtime +7 -delete
	@find data/ -type f -name "*.tmp" -delete
	@echo "Data cleanup completed"

# ============================================================================
# MONITORING & LOGS
# ============================================================================

monitoring:
	@echo "Opening monitoring dashboards..."
	@which open && open http://localhost:3000 || echo "Grafana: http://localhost:3000"
	@which open && open http://localhost:9090 || echo "Prometheus: http://localhost:9090"
	@which open && open http://localhost:3001 || echo "Dashboard: http://localhost:3001"

logs:
	@echo "Recent logs from all services:"
	docker-compose -f docker/compose/docker-compose.yml logs --tail=50

log-follow:
	@echo "Following logs from all services (Ctrl+C to stop):"
	docker-compose -f docker/compose/docker-compose.yml logs -f

log-frigate:
	@echo "Frigate logs:"
	docker-compose -f docker/compose/docker-compose.yml logs -f frigate-plus

# ============================================================================
# MAINTENANCE
# ============================================================================

health:
	@echo "Checking system health..."
	@docker-compose -f docker/compose/docker-compose.yml ps
	@echo ""
	@echo "Service health checks:"
	@docker-compose -f docker/compose/docker-compose.yml exec frigate-plus curl -f http://localhost:5000/api/version || echo "Frigate health check failed"
	@docker-compose -f docker/compose/docker-compose.yml exec timescaledb pg_isready -U security || echo "TimescaleDB health check failed"
	@docker-compose -f docker/compose/docker-compose.yml exec redis-stack redis-cli ping || echo "Redis health check failed"

status:
	@echo "Service status:"
	docker-compose -f docker/compose/docker-compose.yml ps
	@echo ""
	@echo "Resource usage:"
	docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

clean:
	@echo "Cleaning Docker system..."
	docker system prune -f
	docker volume prune -f

prune:
	@echo "Removing unused Docker resources..."
	docker system prune -a -f
	docker volume prune -f
	docker network prune -f

# ============================================================================
# DATABASE
# ============================================================================

db-init:
	@echo "Initializing databases..."
	@docker-compose -f docker/compose/docker-compose.yml exec timescaledb psql -U security -d security_events -f infrastructure/database/init.sql
	@echo "Database initialization completed"

db-reset:
	@echo "WARNING: This will delete ALL data!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Resetting all databases..."; \
		docker-compose -f docker/compose/docker-compose.yml down; \
		docker volume rm ai-security-lab-v4_timescaledb-data || true; \
		docker volume rm ai-security-lab-v4_redis-data || true; \
		docker-compose -f docker/compose/docker-compose.yml up -d timescaledb redis-stack; \
		echo "Databases reset!"; \
	else \
		echo "Operation cancelled"; \
	fi

db-backup:
	@echo "Backing up databases..."
	@mkdir -p backups/databases
	@docker-compose -f docker/compose/docker-compose.yml exec timescaledb pg_dump -U security security_events > backups/databases/security_events_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backup completed"

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

shell-frigate:
	docker-compose -f docker/compose/docker-compose.yml exec frigate-plus /bin/bash

shell-db:
	docker-compose -f docker/compose/docker-compose.yml exec timescaledb /bin/bash

shell-redis:
	docker-compose -f docker/compose/docker-compose.yml exec redis-stack /bin/bash

# Show GPU memory usage
gpu-memory:
	@echo "GPU Memory Usage:"
	@nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk '{print "Used: " $$1 "MB, Total: " $$2 "MB, Usage: " $$1/$$2*100 "%"}'

# Quick system overview
overview:
	@echo "=== AI Security Lab v4.0 Overview ==="
	@echo "Services:"; docker-compose -f docker/compose/docker-compose.yml ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "GPU Status:"; nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv | head -1
	@echo ""
	@echo "Storage Usage:"; df -h | grep -E "(Filesystem|$$(pwd))"
	@echo ""
	@echo "Recent Events:"; docker-compose -f docker/compose/docker-compose.yml logs --tail=5
