# AI Orchestrator Setup Guide

## Virtual Environment Setup

A Python virtual environment has been created for this service.

### Activation

**Activate the virtual environment:**
```bash
cd services/core/ai-orchestrator
source venv/bin/activate
```

### Installed Packages

The following key package has been installed:
- `python-socketio==5.14.3` - For real-time WebSocket communication

### Running the Service

**With virtual environment active:**
```bash
# Make sure you're in the ai-orchestrator directory
cd services/core/ai-orchestrator

# Activate venv
source venv/bin/activate

# Run the service
python main.py
```

The service will start on `http://localhost:8000`

### Deactivation

**To deactivate the virtual environment:**
```bash
deactivate
```

### Installing Additional Dependencies

**To install all requirements:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Note:** Some packages (like torch, CUDA libraries) may require additional system dependencies and will be installed when running in Docker containers.

### Development

The virtual environment is located at:
```
services/core/ai-orchestrator/venv/
```

This directory is excluded from version control via `.gitignore`.

### API Endpoints Available

Once running, you can access:
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Dashboard API:** http://localhost:8000/api/dashboard/overview
- **Socket.IO:** ws://localhost:8000/socket.io/

### Next Steps

1. Ensure other services are running (TimescaleDB, Redis, Frigate)
2. Configure environment variables if needed
3. Start the dashboard frontend: `cd services/ui/dashboard && npm run dev`
4. Access the dashboard at: http://localhost:3000
