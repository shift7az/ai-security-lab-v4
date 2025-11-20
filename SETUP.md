# AI Security Lab v4.0 - Setup Guide

## 🚀 Quick Start

Get the AI Security Lab v4.0 up and running in 10 minutes!

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **NVIDIA GPU** (recommended) with CUDA 11.8+ and nvidia-docker2
- **Python** 3.10+ (for development)
- **Node.js** 18+ (for frontend development)
- At least **16GB RAM** and **50GB disk space**

### Step 1: Clone the Repository

```bash
git clone https://github.com/shift7az/ai-security-lab-v4.git
cd ai-security-lab-v4
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

**CRITICAL:** Update these values in `.env`:
- `POSTGRES_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password
- `JWT_SECRET_KEY` - JWT signing key (min 32 characters!)
- `MINIO_SECRET_KEY` - Object storage password
- `GRAFANA_PASSWORD` - Monitoring dashboard password

**Generate a secure JWT secret:**
```bash
openssl rand -hex 32
```

### Step 3: Deploy the Stack

```bash
# Start all services
docker-compose -f docker/compose/docker-compose.yml up -d

# Check service status
docker-compose -f docker/compose/docker-compose.yml ps
```

### Step 4: Initialize the Database

```bash
# Run database migrations
docker exec -it timescaledb psql -U security -d security_events -f /docker-entrypoint-initdb.d/init.sql
```

### Step 5: Verify AI Models

```bash
# Test AI model initialization
cd services/intelligence/threat-detector
python3 test_models.py
```

**Expected output:**
```
✅ Weapon Detector (YOLOv8): PASSED
✅ Face Detector (MediaPipe): PASSED
✅ Plate Recognizer (EasyOCR): PASSED

🎉 All AI models initialized successfully!
```

### Step 6: Access the Dashboard

Open your browser to:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8001/docs
- **Grafana**: http://localhost:3001

**Default credentials:**
- Username: `admin`
- Password: `admin123` (change immediately!)

---

## 📋 Detailed Installation

### GPU Setup (Recommended)

For GPU-accelerated AI models:

```bash
# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Python Dependencies (Development)

For local development and testing:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install threat detector dependencies
cd services/intelligence/threat-detector
pip install -r requirements.txt

# Install AI model libraries
pip install ultralytics==8.1.0      # YOLOv8
pip install mediapipe==0.10.9        # Face detection
pip install easyocr==1.7.1           # License plate OCR
pip install insightface==0.7.3       # Advanced face recognition (optional)
```

### Frontend Setup (Development)

```bash
cd dashboard
npm install
npm run dev  # Development server on http://localhost:3000
```

---

## 🔧 Configuration

### AI Model Configuration

#### YOLOv8 Weapon Detection

The system will automatically download YOLOv8 models on first run. To use a custom model:

```bash
# Place your custom model in the models directory
cp your-custom-model.pt services/intelligence/threat-detector/models/

# Update .env
YOLO_MODEL=your-custom-model.pt
```

**Model size options:**
- `yolov8n.pt` - Nano (fastest, ~6MB)
- `yolov8s.pt` - Small (balanced, ~22MB)
- `yolov8m.pt` - Medium (accurate, ~52MB)
- `yolov8l.pt` - Large (most accurate, ~87MB)

#### Face Detection

Choose between MediaPipe (fast) or InsightFace (accurate):

```env
# In .env
FACE_DETECTOR_MODEL=mediapipe  # or insightface
```

#### License Plate Recognition

Configure languages for EasyOCR:

```env
# In .env
PLATE_OCR_LANGUAGES=en,es,fr  # Comma-separated language codes
```

### Alert Configuration

#### Webhook Alerts

```env
# In .env
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts
ALERT_THRESHOLD_SCORE=0.7
```

#### Email Alerts

```env
# In .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=security@example.com
SMTP_TO=admin@example.com
```

#### Slack Notifications

```env
# In .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 🧪 Testing

### Run Model Tests

```bash
cd services/intelligence/threat-detector
python3 test_models.py
```

### API Testing

```bash
# Health check
curl http://localhost:8001/health

# Get model info
curl http://localhost:8001/models/info

# Test face detection
curl -X POST http://localhost:8001/detect/faces \
  -H "Content-Type: application/json" \
  -d '{"frame_data": "base64_encoded_image"}'
```

### Run Unit Tests

```bash
# Backend tests
cd services/intelligence/threat-detector
pytest tests/

# Frontend tests
cd dashboard
npm test
```

---

## 📊 Monitoring

### Grafana Dashboards

Access Grafana at http://localhost:3001

**Default credentials:**
- Username: `admin`
- Password: (from `GRAFANA_PASSWORD` in `.env`)

**Pre-configured dashboards:**
- System Health Overview
- Threat Detection Analytics
- AI Model Performance
- Resource Utilization

### Prometheus Metrics

Access metrics at http://localhost:9090

**Key metrics:**
- `threat_detections_total` - Total threat detections
- `model_inference_duration_seconds` - AI model latency
- `api_requests_total` - API request counts
- `gpu_utilization_percent` - GPU usage

---

## 🔒 Security Best Practices

### 1. Change Default Credentials

```bash
# Generate strong passwords
openssl rand -base64 32

# Update in .env:
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - JWT_SECRET_KEY (min 32 chars)
# - MINIO_SECRET_KEY
# - GRAFANA_PASSWORD
```

### 2. Enable HTTPS

```bash
# In .env
ENABLE_HTTPS=true
SSL_CERT_PATH=/certs/fullchain.pem
SSL_KEY_PATH=/certs/privkey.pem

# Use Let's Encrypt for free certificates
sudo certbot certonly --standalone -d yourdomain.com
```

### 3. Configure Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 4. Regular Updates

```bash
# Update Docker images
docker-compose -f docker/compose/docker-compose.yml pull
docker-compose -f docker/compose/docker-compose.yml up -d

# Update AI models
cd services/intelligence/threat-detector
pip install --upgrade ultralytics mediapipe easyocr
```

---

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Verify GPU access
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Restart Docker
sudo systemctl restart docker
```

### Models Not Loading

```bash
# Check model cache
ls -la services/intelligence/threat-detector/models/

# Clear model cache and redownload
rm -rf ~/.cache/torch
rm -rf ~/.cache/mediapipe

# Test model initialization
cd services/intelligence/threat-detector
python3 test_models.py
```

### Database Connection Issues

```bash
# Check database status
docker logs timescaledb

# Reset database
docker-compose -f docker/compose/docker-compose.yml down -v
docker-compose -f docker/compose/docker-compose.yml up -d timescaledb
```

### Memory Issues

```bash
# Increase Docker memory limit
# Edit /etc/docker/daemon.json:
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-shm-size": "2G"
}

sudo systemctl restart docker
```

---

## 📚 Additional Resources

- **Documentation**: [docs/](docs/)
- **API Reference**: [docs/API.md](docs/API.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **AI Models**: [docs/AI_MODELS.md](docs/AI_MODELS.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🆘 Support

- **Issues**: https://github.com/shift7az/ai-security-lab-v4/issues
- **Discussions**: https://github.com/shift7az/ai-security-lab-v4/discussions
- **Email**: support@example.com

---

## ✅ Deployment Checklist

Before going to production:

- [ ] Changed all default passwords
- [ ] Generated secure JWT_SECRET_KEY (32+ chars)
- [ ] Configured database backups
- [ ] Enabled HTTPS with valid certificates
- [ ] Configured firewall rules
- [ ] Set up alert webhooks/email
- [ ] Tested all AI models
- [ ] Configured monitoring dashboards
- [ ] Reviewed security settings
- [ ] Tested disaster recovery
- [ ] Documented custom configuration
- [ ] Trained operators on the system

---

**Ready to deploy? 🚀**

For production deployment, see [DEPLOYMENT.md](docs/DEPLOYMENT.md)
